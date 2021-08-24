from typing import Dict

from pydantic import BaseModel, Field

from .chat import Chat


class User(BaseModel):
    token: str
    name: str
    email: str
    password_hash: str
    chats: Dict[str, Chat] = Field(default_factory=dict)
    bot_tokens: list = Field(default_factory=list)
