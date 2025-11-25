from  fastapi import APIRouter, Body, Depends, BackgroundTasks
from  src.chats.domain.interactions_models import InteractionRequest
from src.app.domain.models.http_responses import CommonHttpResponse
from src.app.middleware.hmac_verification import verify_hmac
from src.llm.state import State
from src.llm.graph import create_graph


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
        final_response="",
        voice=data.voice
    )

    return state

@router.post("/internal/interact", status_code=202, response_model=CommonHttpResponse)
async def secure_interact(
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_hmac),
    state: State = Depends(get_state),
    graph = Depends(create_graph)
):
    
    background_tasks.add_task(graph.ainvoke, state)

    return CommonHttpResponse(
        detail="Request received"
    )
    