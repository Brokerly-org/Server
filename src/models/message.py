from time import time

from pydantic import BaseModel, Field


class Message(BaseModel):
    chat_id: str
    index: int
    sender: str
    content: str
    read_status: bool
    created_at: float = Field(default_factory=time)
