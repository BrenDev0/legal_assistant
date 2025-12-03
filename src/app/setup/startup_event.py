import os
import logging
from src.llm.events.setup import initialize_llm_broker

def startup_event():
    level = os.getenv("LOGGER_LEVEL", logging.INFO)
  
    logging.basicConfig(
        level=int(level),
        format="%(levelname)s - %(name)s - %(message)s"
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    initialize_llm_broker()

    
