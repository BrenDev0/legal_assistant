from fastapi import APIRouter, WebSocket, status, WebSocketDisconnect, Query, Depends
from uuid import UUID
from src.app.middleware.ws_hmac_verification import verify_hmac_ws
from src.web_sockets.connections import WebsocketConnectionsContainer
from src.shared.application.use_cases.ws_streaming import WsStreaming
from src.shared.dependencies.use_cases import get_ws_streaming_use_case
from src.shared.utils.greetings import get_greeting
import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["WebSocket"]
)


@router.websocket("/internal/interact/{chat_id}")
async def websocket_interact(
    websocket: WebSocket, 
    chat_id: UUID,
    voice: bool = Query(False, description="Enable voice mode"),
    stream: WsStreaming = Depends(get_ws_streaming_use_case)
):
    await websocket.accept()
    params = websocket.query_params
    signature = params.get("x-signature")
    payload = params.get("x-payload")

    if not await verify_hmac_ws(signature, payload):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    WebsocketConnectionsContainer.register_connection(chat_id, websocket)
    
    logger.info(f'Websocket connection: {chat_id} opened.')

    if voice:
        greeting = get_greeting()
        
        await stream.execute(
            ws_connection_id=chat_id,
            text=greeting,
            voice=True,
            type="START" 
        )
    try:
        while True: 
            await websocket.receive_text()

    except WebSocketDisconnect:
        WebsocketConnectionsContainer.remove_connection(chat_id)
        logger.info(f'Websocket connection: {chat_id} closed.')