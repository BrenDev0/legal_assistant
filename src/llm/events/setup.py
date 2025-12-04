import os
import threading
import logging
from expertise_chats.broker import Consumer, BrokerConnection

from src.llm.dependencies.handlers import get_incomming_message_handler
logger = logging.getLogger("auth.events.setup")

LLM_QUEUES = [
    ("legal_assistant.incomming", "95e222ef-c637-42d3-a81e-955beeeb0ba2.process")
]

def __setup_llm_incomming_consumer():
    consumer = Consumer(
        queue_name="legal_assistant.incomming",
        handler=get_incomming_message_handler()
    )
    
    thread = threading.Thread(target=consumer.start, daemon=False)
    thread.start()
    logger.info("legal assistant inbound consumer listening")


def __initialize_llm_queues():
    EXCHANGE = os.getenv("EXCHANGE")
    channel = BrokerConnection.get_channel()

    channel.exchange_declare(
        exchange=EXCHANGE,
        exchange_type="topic",
        durable=True
    )


    for queue_name, routing_key in LLM_QUEUES:
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=EXCHANGE,
            queue=queue_name,
            routing_key=routing_key
        )

    logger.info("legal assistant queue initialized")

    __setup_llm_incomming_consumer()


def initialize_llm_broker():
    __initialize_llm_queues()