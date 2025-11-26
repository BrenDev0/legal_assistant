import logging
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

from src.shared.application.use_cases.ws_streaming import WsStreaming
from src.shared.dependencies.services import get_text_to_speech_service, get_ws_transport_service
logger = logging.getLogger(__name__)


def get_ws_streaming_use_case() -> WsStreaming:
    try:
        instance_key = "ws_transport_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = WsStreaming(
            ws_tansport_service=get_ws_transport_service(),
            tts_service=get_text_to_speech_service()
        )
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service