import logging
from expertise_chats.broker import InteractionEvent
from src.llm.events.scehmas import IncommingMessageEvent
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.state import State
from src.llm.domain.models import ContextOrchestratorOutput
from src.llm.domain.services.llm_service import LlmService

logger = logging.getLogger(__name__)

class ContextOrchestrator:
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

   
    def __get_prompt(
        self, 
        chat_history
    ):
        system_message = """
        You are a legal context orchestrator agent. Analyze the user's query to determine what information is needed.

        Set general_law = True if the query requires:
        - Country/jurisdiction laws, statutes, regulations
        - Legal precedents, case law
        - General legal principles or requirements

        Set company_law = True if the query requires:
        - Company-specific documents, policies, contracts
        - Internal legal matters
        - Company compliance status

        Multiple fields can be True simultaneously.

        If the user's query is outside the scope of legal topics, or is too vague or ambiguous to determine the required context, set **all fields to False**.

        Examples:
        - "What are employment laws in Jalisco?" - general_law: True, company_law: False
        - "Review our employment contract" - general_law: False, company_law: True
        - "Is our privacy policy compliant?" - general_law: True, company_law: True
        - "What's the weather today?" - general_law: False, company_law: False
        - "Help" - general_law: False, company_law: False
        """
        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            chat_history=chat_history,
            input=chat_history[0]
        )

        return prompt

    async def interact(self, state: State) -> ContextOrchestratorOutput: 
        try: 
            event = InteractionEvent(**state["event"])
            event_data = IncommingMessageEvent(**event.event_data)  
            prompt = self.__get_prompt(
                chat_history=event_data.chat_history
            )

            response = await self.__llm_service.invoke_structured(
                prompt=prompt,
                response_model=ContextOrchestratorOutput,
                temperature=0.0
            )

            return response
        except Exception as e:
            logger.error(str(e))
            raise