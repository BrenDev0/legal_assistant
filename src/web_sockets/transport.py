from typing import Union, Any
from uuid import UUID
import logging

from src.web_sockets.connections import WebsocketConnectionsContainer
logger = logging.getLogger(__name__)

class WebSocketTransportService:
    @staticmethod
    async def send(
        connection_id: Union[str, UUID],
        data: Any
    ):
        ws = WebsocketConnectionsContainer.resolve_connection(connection_id=str(connection_id))

        if ws:
            try: 
                await ws.send_json(data)
                
            except Exception as e:
                if "closed" in str(e).lower() or "disconnect" in str(e).lower():
                    logger.info(f"Connection {connection_id} disconnected")
                    return
                
                logger.error(f"Connection id: {connection_id}::::, Error sending data:::: {e}")
                raise e