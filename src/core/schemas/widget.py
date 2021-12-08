from sqlmodel import SQLModel, Field


class Widget(SQLModel):
    type: str
    args: dict = Field(default_factory=dict)
