import os
import logging

from expertise_chats.llm import StreamLlmOutput, SearchForContext, LlmServiceAbstract, PromptService

from src.llm.domain.state import State
from src.llm.events.scehmas import IncommingMessageEvent


logger = logging.getLogger(__name__)

class GeneralLegalResearcher:
    def __init__(
        self, 
        stream_llm_output: StreamLlmOutput,
        search_for_context: SearchForContext,
        llm_service: LlmServiceAbstract,
        prompt_service: PromptService

    ):
        self.__llm_service = llm_service
        self.__prompt_service = prompt_service
        self.__stream_llm_output = stream_llm_output
        self.__search_for_context = search_for_context

    async def __get_prompt(self, input: str):
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
            input=input,
            namespace=os.getenv("LEGAL_COLLECTION"),
            top_k=5
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
            prompt = await self.__get_prompt(input=event_data.chat_history[0].text)
            
            if not state["context_orchestrator_response"].company_law:
                response = await self.__stream_llm_output.execute(
                    prompt=prompt,
                    event=event,
                    temperature=0.0,
                )

                return response
            
            response = await self.__llm_service.invoke(
                prompt=prompt,
                temperature=0.0
            )

            self.__producer.publish(
                routing_key="messages.outgoing.send",
                event_message={
                    "llm_response": response
                }
            )

            return response

        except Exception as e:
            logger.error(str(e))
            raise