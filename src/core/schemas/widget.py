from pydantic import BaseModel, Field


class Widget(BaseModel):
    type: str
    args: dict = Field(default_factory=dict)
