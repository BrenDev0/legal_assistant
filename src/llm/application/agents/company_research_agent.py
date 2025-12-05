import logging
from typing import Union
from uuid import UUID
from expertise_chats.llm import SearchForContext, StreamLlmOutput, LlmServiceAbstract, PromptService


from src.llm.domain.state import State
from src.llm.events.scehmas import IncommingMessageEvent


logger = logging.getLogger(__name__)

class CompanyLegalResearcher:
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmServiceAbstract,
        search_for_context: SearchForContext,
        stream_llm_output: StreamLlmOutput
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__search_for_context = search_for_context
        self.__stream_llm_output = stream_llm_output

    async def __get_prompt(
        self,  
        input: str,
        company_id: Union[str, UUID]
    ):
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
        collection_name = f"{company_id}_company_docs"

        context = await self.__search_for_context.execute(
            input=input,
            namespace=collection_name
        )

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input,
            context=context
        )

        return prompt

    async def interact(self, state: State):
        try:
            event = state["event"]
            event_data = IncommingMessageEvent(**event.event_data)
            prompt = await self.__get_prompt(
                company_id=event.company_id,
                input=event_data.chat_history[0].text
            )
            
            
            if not state["context_orchestrator_response"].general_law:
                response = await self.__stream_llm_output.execute(
                    prompt=prompt,
                    event=event.model_copy(),
                    temperature=0.0
                )

                return response
            
            response = await self.__llm_service.invoke(
                prompt=prompt,
                temperature=0.0
            )

            return response
        
        except Exception as e:
            logger.error(str(e))
            raise