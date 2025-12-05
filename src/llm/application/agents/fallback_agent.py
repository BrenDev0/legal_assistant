import logging
from expertise_chats.llm import PromptService, StreamLlmOutput
from src.llm.events.scehmas import IncommingMessageEvent
from src.llm.domain.state import State


logger = logging.getLogger(__name__)

class FallBackAgent:
    def __init__(
        self, 
        prompt_service: PromptService, 
        stream_llm_output: StreamLlmOutput
    ):
        self.__stream_llm_output = stream_llm_output
        self.__prompt_service = prompt_service


    def __get_prompt(
        self,
        input: str
    ):
        system_message = """
        You are a legal assistant fallback agent.

        The user's request has already been determined to be outside the scope of this assistant, or is too vague to answer.

        Politely inform the user that you cannot assist with their request because it is either outside the scope of this assistant or lacks sufficient detail.

        Clearly explain that your expertise is limited to legal topics, including:
        - General legal principles, statutes, and regulations
        - Company-specific legal documents and policies
        - Legal compliance and related matters
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        If the user would like help with a legal question, encourage them to ask about those topics and provide more specific details if possible.
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input
        )

        return prompt


    async def interact(
        self,
        state: State
    ): 
        try:
            event = state["event"]
            event_data = IncommingMessageEvent(**event.event_data)
            prompt = self.__get_prompt(input=event_data.chat_history[0].text)
            

            response = await self.__stream_llm_output.execute(
                prompt=prompt,
                event=event,
                temperature=0.5
            )

            return response
        
        except Exception as e:
            logger.error(str(e))
            raise
        