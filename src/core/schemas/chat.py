from pydantic import BaseModel, Field


class Chat(BaseModel):
    id: str
    user_token: str
    botname: str
    active: bool = True
    size: int = 0
    bot_messages: list = Field(default_factory=list)
    bot_unread_messages: list = Field(default_factory=list)
    user_messages: list = Field(default_factory=list)
    user_unread_messages: list = Field(default_factory=list)
