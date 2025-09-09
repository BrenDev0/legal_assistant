from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.utils.decorators.error_hanlder import error_handler
from src.workflow.state import State

class ResearchAggregator: 
    __MODULE = "research_aggregator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(self, state: State):  
        context_parts = []
        
        if state.get('general_legal_response'):
            context_parts.append(f"GENERAL LEGAL RESEARCH:\n{state['general_legal_response']}")
        
        if state.get('company_legal_response'):
            context_parts.append(f"COMPANY LEGAL RESEARCH:\n{state['company_legal_response']}")
        
        if state.get('chat_history_response'):
            context_parts.append(f"CHAT HISTORY CONTEXT:\n{state['chat_history_response']}")

        # Join all available context
        combined_context = "\n\n".join(context_parts) if context_parts else "No additional research context available."

        system_message = f"""
        You are a Legal Research Aggregator. Synthesize research from multiple sources into a comprehensive response for the user's legal query.

        ## Guidelines:
        - Combine all available research sources
        - Distinguish between general law and company-specific requirements
        - Reference previous conversations when relevant
        - Provide actionable guidance with proper citations

        ## Available Research:
        {combined_context}

        Synthesize the above research to provide a comprehensive legal response.
        """

        prompt = await self.__prompt_service.custom_prompt_template(
            state=state,
            system_message=system_message,
            with_chat_history=True
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(self, state: State) -> str:
        llm = self.__llm_service.get_llm(temperature=0.5, max_tokens=350)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm
        
        response = await chain.ainvoke({"input": state["input"]})

        return response.content.strip()