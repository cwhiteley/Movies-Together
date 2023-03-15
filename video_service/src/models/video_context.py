from typing import Any
from pydantic import BaseModel


class VideoContext(BaseModel):
    active_connections: set = set()
    paused: bool = False
    current_time: int = 0
    send_current_time: Any = None
    save_current_time: Any = None
