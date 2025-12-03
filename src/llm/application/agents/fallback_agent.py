import logging
from expertise_chats.broker import Producer, InteractionEvent
from expertise_chats.schemas.ws import WsPayload
from src.llm.application.services.prompt_service import PromptService
from src.llm.domain.services.llm_service import LlmService
from src.llm.events.scehmas import IncommingMessageEvent
from src.llm.domain.state import State
from src.shared.utils.decorators.error_hanlder import error_handler
logger = logging.getLogger(__name__)

class FallBackAgent:
    __MODULE = "fallback.agent"
    def __init__(
        self, 
        prompt_service: PromptService, 
        llm_service: LlmService,
        producer: Producer
    ):
        self.__prompt_service = prompt_service
        self.__llm_service = llm_service
        self.__producer = producer

    @error_handler(module=__MODULE)
    def __get_prompt(
        self,
        input: str
    ):
        system_message = """
        You are a legal assistant fallback agent.

        The user's request has already been determined to be outside the scope of this assistant, or is too vague to answer.

        Politely inform the user that you cannot assist with their request because it is either outside the scope of this assistant or lacks sufficient detail.

        Clearly explain that your expertise is limited to legal topics, including:
        - General legal principles, statutes, and regulations
        - Company-specific legal documents and policies
        - Legal compliance and related matters
        - **Format your response using valid Markdown. Use headings, bullet points, numbers, indentations, and bold or italics for clarity.**

        If the user would like help with a legal question, encourage them to ask about those topics and provide more specific details if possible.
        """

        prompt = self.__prompt_service.build_prompt(
            system_message=system_message,
            input=input
        )

        return prompt

    @error_handler(module=__MODULE)
    async def interact(
        self,
        state: State
    ): 
        event = InteractionEvent(**state["event"])
        event_data = IncommingMessageEvent(**event.event_data)
        prompt = self.__get_prompt(input=event_data.chat_history[0])
        

        chunks = []
        sentence = ""
        async for chunk in self.__llm_service.generate_stream(
            prompt=prompt,
            temperature=0.5
        ):
            chunks.append(chunk)
            
            if event.voice:
                sentence += chunk
                # Check for sentence-ending punctuation
                if any(p in chunk for p in [".", "?", "!"]) and len(sentence) > 10:
                    ws_payload = WsPayload(
                        type="AUIDO",
                        data=sentence.strip()
                    )

                    event.event_data = ws_payload.model_dump()

                    self.__producer.publish(
                        routing_key="streaming.audio.outbound.send",
                        event_message=event
                    )

                    sentence = ""
            else:
                ws_payload = WsPayload(
                    type="TEXT",
                    data=chunk
                )

                event.event_data = ws_payload

                self.__producer.publish(
                    routing_key="streaming.general.outbound.send",
                    event_message=event
                )
                
        # After streaming all chunks, send any remaining text for voice
        if event.voice and sentence.strip():
            ws_payload = WsPayload(
                type="AUIDO",
                data=sentence.strip()
            )

            event.event_data = ws_payload.model_dump()

            self.__producer.publish(
                routing_key="streaming.audio.outbound.send",
                event_message=event
            )

            ws_payload.type = "TEXT"
            ws_payload.data = chunk

            event.event_data = ws_payload.model_dump()

            self.__producer.publish(
                routing_key="streaming.general.outbound.send",
                event_message=event
            )


        self.__producer.publish(
            routing_key="messages.outgoing.send",
            event_message={
                "llm_response": "".join(chunks)
            }
        )    
        return "".join(chunks)
        
        