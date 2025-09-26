from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.api.modules.websocket.websocket_service import WebsocketService
from src.utils.decorators.error_hanlder import error_handler
from src.workflow.state import State
from fastapi import WebSocket, WebSocketDisconnect

class ResearchAggregator: 
    __MODULE = "research_aggregator.agent"
    def __init__(self, prompt_service: PromptService, llm_service: LlmService, websocket_service: WebsocketService):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__websocket_service = websocket_service

    @error_handler(module=__MODULE)
    async def __get_prompt_template(self, state: State):  
        context_parts = []
        
        if state.get('general_legal_response'):
            context_parts.append(f"GENERAL LEGAL RESEARCH:\n{state['general_legal_response']}")
        
        if state.get('company_legal_response'):
            context_parts.append(f"COMPANY LEGAL RESEARCH:\n{state['company_legal_response']}")
        
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
        # Do not call agent unless  multiple context needs to  be combined
        general = state.get("general_legal_response", None)
        company = state.get("company_legal_response", None)
        
        if general and not company:
            return general.strip()
        if company and not general:
            return company.strip()
        

        # Call agent to compose a reposnse  based on the context
        llm = self.__llm_service.get_llm(temperature=0.5, max_tokens=2000)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm
        
        websocket: WebSocket = self.__websocket_service.get_connection(state["chat_id"])
        
        chunks = []
        try:
           async for chunk in chain.astream({"input": state["input"]}):
                if websocket:
                    try:
                       await websocket.send_json(chunk.content)
                    except WebSocketDisconnect:
                       self.__websocket_service.remove_connection(state["chat_id"])
                       websocket = None
                    
                chunks.append(chunk.content)
               
        except Exception as e:
            print(f"Error during streaming: {e}")
            raise

        finally:
            return "".join(chunks)
