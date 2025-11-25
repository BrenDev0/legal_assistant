import logging
from websockets import ConnectionClosed
from typing import Union, Any
from uuid import UUID
from src.web_sockets.connections import WebsocketConnectionsContainer
logger = logging.getLogger(__name__)

class WebSocketTransportService:
    @staticmethod
    async def send(
        connection_id: Union[str, UUID],
        data: Any
    ):
        ws = WebsocketConnectionsContainer.resolve_connection(connection_id=connection_id)

        if ws:
            try: 
                await ws.send_json(data)
            
            except ConnectionClosed:
                logger.info(f"Connection {connection_id} disconnected")

            except Exception as e:
                logger.info(f"Connection id: {connection_id}::::, Error sending data:::: {e}")
                raise e