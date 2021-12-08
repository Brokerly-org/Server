from time import time

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from .widget import Widget


class InputMessage(BaseModel):
    text: str
    widget: Widget = None


class Message(SQLModel, table=True):
    index: int = Field(default=None, primary_key=True)
    chat_id: str = Field(default=None, foreign_key="chat.id")
    sender: str
    read_status: bool
    created_at: float = Field(default_factory=time)

    content: str
    # widget: Widget = None
