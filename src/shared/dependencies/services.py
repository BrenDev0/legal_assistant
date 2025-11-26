import logging
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

logger = logging.getLogger(__name__)
from src.shared.domain.services.speech_to_text import SpeechToText
from src.shared.domain.services.text_to_speech import TextToSpeech
from src.shared.infrastructure.services.deepgram_stt_service import DeepgramSpeechToTextService
from src.web_sockets.transport import WebSocketTransportService

from src.shared.infrastructure.services.deepgram_tts_service import DeepgramTextToSpeechService

def get_ws_transport_service() -> WebSocketTransportService:
    try:
        instance_key = "ws_transport_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = WebSocketTransportService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service


def get_speech_to_text_service() -> SpeechToText:
    try:
        instance_key = "stt_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = DeepgramSpeechToTextService(
            model="nova",
            language="es"
        )
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service

    

def get_text_to_speech_service() -> TextToSpeech:
    try:
        instance_key = "tts_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = DeepgramTextToSpeechService(
            model="aura-2-celeste-es"
        )
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service
 

