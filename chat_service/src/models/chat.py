from datetime import time
from typing import List

from pydantic import BaseModel


class Message(BaseModel):
    timestamp: time = None
    user: str = None
    data: str = None

    class Config:
        orm_mode = True


class Chat(BaseModel):
    id: str = None
    messages: List[Message] = []

    class Config:
        orm_mode = True
