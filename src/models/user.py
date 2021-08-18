from typing import Dict

from pydantic import BaseModel, Field

from .chat import Chat


class User(BaseModel):
    token: str
    name: str
    email: str
    password: str
    chats: Dict[str, Chat] = Field(default_factory=dict)
    bot_tokens: list = Field(default_factory=list)

    def add_bot(self, bot_token: str):
        self.bot_tokens.append(bot_token)

    def add_chat(self, chat: Chat):
        self.chats[chat.botname] = chat

    def push_to_bot(self, botname: str, message: str):
        self.chats[botname].user_push(message)

    def pull_from_chats(self):
        new_messages = []
        for chat in self.chats.values():
            chat_messages = chat.user_pull()
            if not chat_messages:
                continue
            new_messages.append({"botname": chat.botname, "messages": chat_messages})
        return new_messages

    def delete(self):
        for chat in self.chats.values():
            chat.close()
        # TODO: remove user

