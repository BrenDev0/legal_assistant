from typing import Any, Dict
from expertise_chats.broker import AsyncEventHandlerBase, InteractionEvent
from src.llm.domain.state import State
from src.llm.domain.services.workflow_service import WorkflowService

class IncommingMessageHandler(AsyncEventHandlerBase):
    def __init__(
        self,
        workflow_service: WorkflowService
    ):
        self.__workflow_service = workflow_service

    async def handle(self, payload: Dict[str, Any]):
        event = InteractionEvent(payload)
        
        state = State(
            context_orchestrator_response=None,
            general_legal_response="",
            company_legal_response="",
            final_response="",
            event=event
        )

        await self.__workflow_service.invoke_workflow(
            state=state
        )

