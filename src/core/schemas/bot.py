from typing import Dict

from pydantic import BaseModel, Field

from .chat import Chat


class Bot(BaseModel):
    token: str
    owner_token: str
    botname: str
    title: str
    description: str
    last_online: float = 0
    chats: Dict[str, Chat] = Field(default_factory=dict)
