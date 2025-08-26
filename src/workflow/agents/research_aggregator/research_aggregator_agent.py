from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.utils.decorators.error_hanlder import error_handler
from src.workflow.state import State
from src.api.modules.websocket.websockets_service import WebsocketService

class ResearchAggregator: 
    __MODULE = "research_aggregator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService, websockets_service: WebsocketService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__websockets_service = websockets_service

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

        ## Response Structure:
        **Legal Overview:** Brief summary addressing the question
        **Applicable Law:** Mexican legal provisions (if available)
        **Company Policy:** Internal requirements (if available)
        **Previous Discussion:** Chat history context (if relevant)
        **Recommendations:** Practical next steps

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
        llm = self.__llm_service.get_llm(temperature=0.5, max_tokens=2500)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm
        
        response = await chain.astream({"input": state["input"]})

        return response.content.strip()