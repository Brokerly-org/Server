from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


class Bot(SQLModel, table=True):
    token: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    botname: str
    title: str
    description: str
    owner_token: str = Field(default=None, foreign_key="user.token")
    online_status: Optional[bool] = False
    # chats: Dict[str, Chat] = Field(default_factory=dict)

