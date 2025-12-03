from pydantic import BaseModel
from typing import List
from src.llm.domain.entities import Message

class IncommingMessageEvent(BaseModel):
    chat_id: str
    company_id: str
    chat_history: List[Message]