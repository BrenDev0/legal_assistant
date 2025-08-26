from fastapi import APIRouter, WebSocket, status
from uuid import uuid4
from src.api.modules.websocket.ws_hmac_verification import verify_hmac_ws


router = APIRouter()


@router.websocket("/ws/secure/interact/{connection_id}")
async def websocket_interact(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    signature = params.get("x-signature")
    payload = params.get("x-payload")
    if not await verify_hmac_ws(signature, payload):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Generate a connection/session ID and send to client
    connection_id = str(uuid4())
    await websocket.send_json({"connection_id": connection_id})

    # Example: Echo messages back to the client
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except Exception:
        await websocket.close()