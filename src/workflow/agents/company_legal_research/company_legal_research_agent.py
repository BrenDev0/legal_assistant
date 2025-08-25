from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State

class CompanyLegalResearcher:
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    async def __get_prompt_template(self, state: State):
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

        Analyze the query using the company's legal documents and provide relevant internal legal context.
        """
        collection_name = f"{state['company_id']}_company_docs"
        prompt = await self.__prompt_service.custom_prompt_template(state=state, system_message=system_message, with_context=True, context_collection=collection_name)

        return prompt

    async def interact(self, state: State):
        llm = self.__llm_service.get_llm(temperature=0.5, max_token=2000)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm
        
        response = await chain.ainvoke({"input": state["input"]})

        return response.content.strip()