from time import time

from pydantic import BaseModel, Field

from .widget import Widget


class InputMessage(BaseModel):
    text: str
    widget: Widget = None


class Message(BaseModel):
    chat_id: str
    index: int
    sender: str
    read_status: bool
    created_at: float = Field(default_factory=time)

    content: str
    widget: Widget = None
