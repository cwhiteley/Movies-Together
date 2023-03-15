from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, Json, create_model

class Message(BaseModel):
    timestamp: datetime = None
    user: str = None
    data: str = None

    class Config:
        orm_mode = True

class Chat(BaseModel):
    id: str = None
    messages: List[Message] = []

    class Config:
        orm_mode = True

