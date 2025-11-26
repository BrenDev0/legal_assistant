import logging
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

from src.web_sockets.transport import WebSocketTransportService
logger = logging.getLogger(__name__)


def get_ws_transport_service() -> WebSocketTransportService:
    try:
        instance_key = "ws_transport_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = WebSocketTransportService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service