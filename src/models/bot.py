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

    def add_chat(self, chat: Chat):
        self.chats[chat.id] = chat

    def push_to_chat(self, chat_id: str, message: str):
        self.chats[chat_id].bot_push(message)

    def pull_from_chats(self):
        new_messages = []
        for chat in self.chats.values():
            new_messages.append({"chat": chat.id, "messages": chat.bot_pull()})
        return new_messages

    def delete(self):
        for chat in self.chats.values():
            chat.close()
