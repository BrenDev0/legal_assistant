from   pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

class EmbeddingConfig(BaseModel):
    model_name: str = "text-embedding-3-large"
    distance_metric: str = "cosine"
    vector_size: int = 3072  

class SearchResult(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float

class Message(BaseModel):
    text: Optional[str] = None
    json_data: Optional[Any] = None
    message_type: str