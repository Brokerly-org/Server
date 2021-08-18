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

    def bot_push(self, message: str):
        self.user_unread_messages.append(message)

    def user_push(self, message: str):
        self.bot_unread_messages.append(message)

    def bot_pull(self):
        new_messages = self.bot_unread_messages.copy()
        self.bot_messages.extend(self.bot_unread_messages)
        self.bot_unread_messages.clear()
        return new_messages

    def user_pull(self) -> list:
        new_messages = self.user_unread_messages.copy()
        self.user_messages.extend(self.user_unread_messages)
        self.user_unread_messages.clear()
        return new_messages

    def close(self):
        self.active = False
