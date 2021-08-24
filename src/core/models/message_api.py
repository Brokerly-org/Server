from typing import Callable
from collections import defaultdict
from uuid import UUID

from core.models.database import DB
from core.models.orm import load_chat_by_botname_and_user_token, load_chat_by_id, create_message
from core.schemas.bot import Bot
from core.schemas.user import User
from core.schemas.message import InputMessage


class MessageApi:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("DataApi not initialize")
        return cls._instance

    def __init__(self):
        self.db: DB = DB.get_instance()
        self.listeners = defaultdict(dict)

        self.__class__._instance = self

    async def _notify_listeners(self, token: str):
        callbacks = self.listeners[token].values()
        for callback in callbacks:
            await callback()

    async def bot_push(self, bot: Bot, chat_id: str, message: InputMessage):
        chat = await load_chat_by_id(chat_id)
        if chat is None:
            raise KeyError
        if chat.botname != bot.botname:
            raise KeyError
        await create_message(chat.id, chat.size, "bot", message)
        await self._notify_listeners(chat.user_token)

    async def user_push(self, user: User, botname: str, message: str):
        chat = await load_chat_by_botname_and_user_token(botname, user.token)
        if chat is None:
            raise KeyError  # TODO: replace with costume exception
        message = InputMessage(text=message)
        await create_message(chat.id, chat.size, "user", message)
        await self._notify_listeners(botname)

    def listen_on(self, token: str, callback: Callable, session_id: UUID):
        self.listeners[token][session_id] = callback

    def remove_listener(self, token: str, session_id: UUID):
        del self.listeners[token][session_id]
