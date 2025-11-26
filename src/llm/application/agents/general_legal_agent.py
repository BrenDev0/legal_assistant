import os
import logging
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.services.llm_service import LlmService
from src.llm.domain.state import State
from src.shared.utils.decorators.error_hanlder import error_handler
from src.llm.application.use_cases.search_for_context import SearchForContext
from src.shared.application.use_cases.ws_streaming import WsStreaming
logger = logging.getLogger(__name__)

class GeneralLegalResearcher:
    __MODULE = "general_legal_research.agent"
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

    @error_handler(module=__MODULE)
    async def __get_prompt(self, state: State):
        system_message = """
        You are a Mexican Legal Research Expert. Analyze the user's query and provide relevant legal context using the provided Mexican legal documents.

        ## Your Role:
        - Extract relevant legal provisions from the context documents
        - Provide structured legal analysis with proper citations
        - Focus on current, applicable Mexican law

        ## Guidelines:
        - Use provided context documents as primary source
        - Include specific article numbers and legal references
        - Consider federal vs. state jurisdiction when relevant
        - Provide factual legal context, not legal advice
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        Analyze the query and provide comprehensive Mexican legal context using the available legal documents.
        """
        context = await self.__search_for_context.execute(
            input=state["input"],
            namespace=os.getenv("LEGAL_COLLECTION")
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
        if not state["context_orchestrator_response"].company_law:
            chunks = []
            sentence = "" 
            async for chunk in self.__llm_service.generate_stream(
                prompt=prompt,
                temperature=0.5
            ):
                chunks.append(chunk)
                if state.get("voice"):
                    sentence += chunk
                    # Check for sentence-ending punctuation
                    if any(p in chunk for p in [".", "?", "!"]) and len(sentence) > 10:
                        await self.__streaming.execute(
                            ws_connection_id=state["chat_id"],
                            text=sentence.strip(),
                            voice=True
                        )
                        sentence = ""
                else: 
                    try:
                        await self.__streaming.execute(
                            ws_connection_id=state["chat_id"],
                            text=chunk,
                            voice=False
                        )  
                    except Exception as e:
                        logger.error(f"error sending chunk: {chunk} :::: {str(e)}")
            # After streaming all chunks, send any remaining text for voice
            if state.get("voice") and sentence.strip():
                try:
                    await self.__streaming.execute(
                        ws_connection_id=state["chat_id"],
                        text=sentence.strip(),
                        voice=True
                    )
                
                    await self.__streaming.execute(
                        ws_connection_id=state["chat_id"],
                        text="END STREAM",
                        voice=True,
                        type="END"
                    )
                except Exception as e:
                    logger.error(f"error sending chunk: {sentence.strip()} :::: {str(e)}")
            return "".join(chunks)
        
        response = await self.__llm_service.invoke(
            prompt=prompt,
            temperature=0.0
        )

        return response