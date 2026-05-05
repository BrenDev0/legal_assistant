from pydantic import BaseModel
from typing import List
from expertise_chats.llm import MessageModel

class IncommingMessageEvent(BaseModel):
    chat_history: List[MessageModel]