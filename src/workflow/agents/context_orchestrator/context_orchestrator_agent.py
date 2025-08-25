from src.workflow.services.prompt_service import PromptService
from langchain_openai import ChatOpenAI
from src.workflow.state import State
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput
from src.workflow.services.llm_service import LlmService
from src.utils.decorators.error_hanlder import error_handler

class ContextOrchestrator:
    __MODULE = "context_orchestrator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(self, state: State):
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

        Set chat_history = True if the query requires:
        - Reference to previous conversations
        - Follow-up questions about earlier topics
        - Context from past interactions

        Multiple fields can be True simultaneously.

        Examples:
        - "What are employment laws in Jalisco?" - general_law: True, company_law: False, chat_history: False
        - "Review our employment contract" - general_law: False, company_law: True, chat_history: False
        - "Is our privacy policy compliant?" - general_law: True, company_law: True, chat_history: False
        - "Can you elaborate on what you mentioned earlier?" - general_law: False, company_law: False, chat_history: True
        """
        prompt = await self.__prompt_service.custom_prompt_template(state=state, system_message=system_message, with_chat_history=True)

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> ContextOrchestratorOutput:
        llm = self.__llm_service.get_llm(temperature=0.5)
        
        prompt = await self.__get_prompt_template(state)
        
        structured_llm = llm.with_structured_output(ContextOrchestratorOutput)
        
        chain = prompt | structured_llm
        
        response = await chain.ainvoke({"input": state["input"]})

        return response