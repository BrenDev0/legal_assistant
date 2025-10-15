from src.workflow.application.services.prompt_service import PromptService
from src.workflow.domain.services.llm_service import LlmService
from src.workflow.state import State
from src.shared.application.use_cases.ws_streaming import WsStreaming
from src.workflow.application.use_cases.search_for_context import SearchForContext
from src.utils.decorators.error_hanlder import error_handler

class CompanyLegalResearcher:
    __MODULE = "company_research.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        streaming: WsStreaming,
        search_for_context: SearchForContext
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__streaming = streaming
        self.__search_for_context = search_for_context

    async def __get_prompt(self, state: State):
        system_message = """
        You are a Company Legal Document Specialist. Analyze the user's query using the provided company documents and policies.

        ## Your Role:
        - Extract relevant provisions from company contracts and policies
        - Assess compliance status based on internal documents
        - Identify policy requirements and gaps

        ## Guidelines:
        - Focus on company's internal legal documents
        - Use provided context as primary source
        - Reference actual document sections
        - Provide factual information only
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        Analyze the query using the company's legal documents and provide relevant internal legal context.

        If there is no context found you will state that you've found no company documnets to analyze
        """
        collection_name = f"{state['company_id']}_company_docs"

        context = await self.__search_for_context.execute(
            input=state["input"],
            namespace=collection_name
        )

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=state["input"],
            context=context
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State):
        prompt = await self.__get_prompt(state)
        
        if not state["context_orchestrator_response"].general_law:
            chunks = []
            async for chunk in self.__llm_service.generate_stream(
                prompt=prompt,
                temperature=0.0
            ):
                chunks.append(chunk)
                if state["voice"]:
                    sentence += chunk
                    # Check for sentence-ending punctuation
                    if any(p in chunk for p in [".", "?", "!"]) and len(sentence) > 10:
                        await self.__streaming.execute(
                            ws_connection_id=state["chat_id"],
                            text=sentence.strip(),
                            voice=True
                        )
                        sentence = ""

                    # Send any remaining text after the stream ends
                    if sentence.strip():
                        await self.__streaming.execute(
                            ws_connection_id=state["chat_id"],
                            text=sentence.strip(),
                            voice=True
                        )
                else: 
                    await self.__streaming.execute(
                        ws_connection_id=state["chat_id"],
                        text=chunk,
                        voice=False
                    )
                
                    return "".join(chunks)
        
        response = await self.__llm_service.invoke(
            prompt=prompt,
            temperature=0.0
        )

        return response