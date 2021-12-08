from uuid import uuid4

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    token: str = Field(primary_key=True, default_factory=lambda: str(uuid4()))
    name: str
    email: str
    password_hash: str
