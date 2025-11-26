import logging

from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered
from src.voice.domain.services.speech_to_text import SpeechToText
from src.voice.domain.services.text_to_speech import TextToSpeech

from src.voice.infrastructure.deepgram.stt_service import DeepgramSpeechToTextService
from src.voice.infrastructure.deepgram.tts_service import DeepgramTextToSpeechService
logger = logging.getLogger(__name__)

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
 

