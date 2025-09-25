from fastapi import WebSocket, WebSocketDisconnect

from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State

from src.api.modules.websocket.websocket_service import WebsocketService

class CompanyLegalResearcher:
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        websocket_service: WebsocketService
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__websocket_service = websocket_service

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

        If there is no context found you will state that you've found no company documnets to analyze
        """
        collection_name = f"{state['company_id']}_company_docs"
        prompt = await self.__prompt_service.custom_prompt_template(state=state, system_message=system_message, with_context=True, context_collection=collection_name)

        return prompt

    async def interact(self, state: State):
        llm = self.__llm_service.get_llm(temperature=0.1, max_tokens=350)
        
        prompt = await self.__get_prompt_template(state)
        
        chain = prompt | llm

        if not state["context_orchestrator_response"].general_law:
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
                return " ".join(chunks)
        
        response = await chain.ainvoke({"input": state["input"]})

        return response.content.strip()