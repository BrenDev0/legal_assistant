import logging
from typing import Any, Dict
from expertise_chats.broker import AsyncEventHandlerBase, InteractionEvent
from expertise_chats.errors.error_handler import handle_error
from src.llm.domain.state import State
from src.llm.domain.services.workflow_service import WorkflowService
from src.llm.dependencies.producers import get_producer

logger = logging.getLogger(__name__)

class IncommingMessageHandler(AsyncEventHandlerBase):
    def __init__(
        self,
        workflow_service: WorkflowService
    ):
        self.__workflow_service = workflow_service

    async def handle(self, payload: Dict[str, Any]):
        logger.debug(f"legal assistant history handler received request ::: {payload}")

        try:
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
        except Exception as e: 
            logger.error(str(e))
            handle_error(
                event=event,
                producer=get_producer(),
                server_error=True
            )

