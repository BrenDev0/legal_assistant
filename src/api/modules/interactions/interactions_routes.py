from  fastapi import APIRouter, Body, Request, Depends
from  src.api.modules.interactions.interactions_models import InteractionRequest
from src.api.core.middleware.hmac_verification import verify_hmac
from src.workflow.state import State
from src.workflow.graph import create_graph
from src.api.modules.interactions.interactions_controller import InteractionsController
from src.dependencies.container import Container

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

async def get_state(data: InteractionRequest = Body(...)):
    state = State(
        company_id=data.company_id,
        chat_history=data.chat_history,
        input=data.input,
        context_orchestrator_response=None,
        general_legal_response="",
        company_legal_response="",
        final_response=""
    )

    return state

def get_graph():
    return create_graph()

def get_controller() -> InteractionsController:
    controller = Container.resolve("interactions_controller")
    return controller

@router.post("/internal/interact", status_code=200, response_model=State)
async def secure_interact(
    req: Request,
    _: None = Depends(verify_hmac),
    state: State = Depends(get_state),
    graph = Depends(get_graph),
    controller: InteractionsController = Depends(get_controller)
):
    return await controller.interact(
        req=req,
        state=state,
        graph=graph
    )