from typing import Union
from uuid import UUID
import logging
from src.shared.domain.services.text_to_speech import TextToSpeech
from src.web_sockets.transport import WebSocketTransportService
logger = logging.getLogger(__name__)

class WsStreaming():
    def __init__(
        self,
        tts_service: TextToSpeech,
        ws_tansport_service: WebSocketTransportService
    ):
        self.__tts_service = tts_service
        self.__ws_tranport_service = ws_tansport_service

    
    async def execute(
        self, 
        ws_connection_id: Union[UUID, str],
        text: str,
        voice: bool = False,
        type: str = "audio_response", 
    ):
        if voice:
            if type == "END":
                try:
                    await self.__ws_tranport_service.send(ws_connection_id,{
                        "type": type
                    })
                    return 
                except Exception as e:
                    logger.info(str(e))
                    return 
                
            audio_chunk = self.__tts_service.transcribe(text)
            try:
                await self.__ws_tranport_service.send(ws_connection_id,{
                    "type": type,
                    "audio_data": audio_chunk
                })
            except Exception as e:
                logger.info(str(e))
                return 
        
        else: 
            await self.__ws_tranport_service.send(ws_connection_id, text)

        