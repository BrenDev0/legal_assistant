from  fastapi import APIRouter, Body, Request, Depends
from  src.api.modules.interactions.interactions_models import InteractionRequest
from src.api.core.models.http_responses import CommonHttpResponse
from src.api.core.middleware.hmac_verification import verify_hmac
from src.workflow.state import State
from src.workflow.graph import create_graph
from src.api.modules.interactions.interactions_controller import InteractionsController
from src.api.modules.interactions.interactions_dependencies import get_interactions_controller

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

async def get_state(data: InteractionRequest = Body(...)):
    state = State(
        company_id=data.company_id,
        chat_history=data.chat_history,
        chat_id=data.chat_id,
        input=data.input,
        context_orchestrator_response=None,
        general_legal_response="",
        company_legal_response="",
        final_response=""
    )

    return state

@router.post("/internal/interact", status_code=200, response_model=CommonHttpResponse)
async def secure_interact(
    req: Request,
    _: None = Depends(verify_hmac),
    state: State = Depends(get_state),
    graph = Depends(create_graph),
    controller: InteractionsController = Depends(get_interactions_controller)
):
    return await controller.interact(
        req=req,
        state=state,
        graph=graph
    )