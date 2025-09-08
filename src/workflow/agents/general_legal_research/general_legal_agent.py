from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from src.utils.decorators.error_hanlder import error_handler
import os


class GeneralLegalResearcher:
    __MODULE = "general_legal_research.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(self, state: State):
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

        Analyze the query and provide comprehensive Mexican legal context using the available legal documents.
        """
         
        prompt = await self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message,
            with_context=True,
            context_collection=os.getenv("LEGAL_COLLECTION")
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> str:
        llm = self.__llm_service.get_llm(temperature=0.1, max_tokens=2500)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm
        
        response = await chain.ainvoke({"input": state["input"]})

        return response.content.strip()