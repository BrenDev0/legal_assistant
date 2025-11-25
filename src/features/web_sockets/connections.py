import logging
from typing import Union, Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)

class WebsocketConnectionsContainer:
    _active_connections: Dict[str, Any] = {}

    @classmethod
    def register_connection(cls, connection_id: Union[UUID, str], websocket: Any):
        key = str(connection_id)
        cls._active_connections[key] = websocket
        logger.info(f"connection {key} added.")
        return
    
    @classmethod
    def resolve_connection(cls, connection_id: Union[UUID, str]) -> Any:
        key = str(connection_id)
        connection = cls._active_connections.get(key)
        if not connection:
            logger.info(f"Connection {key} not found in get_connection()")
            return None

        return connection

    @classmethod
    def remove_connection(cls, connection_id: Union[UUID, str]):
        key = str(connection_id)
        cls._active_connections.pop(key, None)
        logger.info(f'Connection: {key} was removed.')