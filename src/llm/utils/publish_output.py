from expertise_chats.schemas.ws import WsPayload
from expertise_chats.broker import InteractionEvent
from src.llm.dependencies.producers import get_producer

def publish_llm_output(
    event: InteractionEvent,
    payload: WsPayload
):
    producer = get_producer()
    event.event_data = payload.model_dump()

    producer.publish(
        routing_key="streaming.audio.outbound.send",
        event_message=event
    )