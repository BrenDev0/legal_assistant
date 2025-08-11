from src.workflow.services.prompt_service import PromptService
from langchain_openai import ChatOpenAI
from src.workflow.state import State
from src.workflow.agents.routing.routing_agent_models import MainRouterOutput

class RoutingAgent:
    def __init__(self, prompt_service: PromptService):
        self.__prompt_service = prompt_service

    def __get_prompt_template(self, state: State):
        system_message = """
        Youre job is to determine what infomation willbe needed to answer the users query.
        You will use the context of the conversation to guide your decision.
        """
        prompt = self.__prompt_service.custom_prompt_chat_history_template(state=state, system_message=system_message)

        return prompt

    async def interact(self, llm: ChatOpenAI, state: State) -> str:
        prompt = self.__get_prompt_template(state)
        
        structured_llm = llm.with_structured_output(MainRouterOutput)
        
        chain = prompt | structured_llm
        
        response = await chain.ainvoke({"input": state["input"]})

        return response.content.strip()