from uuid import uuid4

from sqlmodel import SQLModel, Field


class Chat(SQLModel, table=True):
    id: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    user_token: str = Field(default=None, foreign_key="user.token")
    botname: str = Field(default=None, foreign_key="bot.botname")
    active: bool = True
    size: int = 0
    # bot_messages: list = Field(default_factory=list)
    # bot_unread_messages: list = Field(default_factory=list)
    # user_messages: List[int] = Field(default_factory=list)
    # user_unread_messages: list = Field(default_factory=list)
