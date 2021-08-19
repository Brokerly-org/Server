from typing import Callable
from collections import defaultdict
from uuid import UUID

from db import DB

from models import User, Bot
from data_layer.user import get_bot_by_bot_name


class DataApi:
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

    async def bot_push(self, bot: Bot, chat_id: str, message: str):
        chat = await self.db.get_chat_by_chat_id(chat_id)
        await self.db.create_message(chat.id, chat.size, "bot", message)
        user_token = chat.user_token
        await self._notify_listeners(user_token)

    async def user_push(self, user: User, botname: str, message: str):
        chat = await self.db.get_chat_by_user_token_and_botname(user.token, botname)
        if chat is None:
            raise KeyError  # TODO: replace with costume exception
        await self.db.create_message(chat.id, chat.size, "user", message)
        bot = await get_bot_by_bot_name(chat.botname)
        bot_token = bot.token
        await self._notify_listeners(bot_token)

    def listen_on(self, token: str, callback: Callable, session_id: UUID):
        self.listeners[token][session_id] = callback

    def remove_listener(self, token: str, session_id: UUID):
        del self.listeners[token][session_id]
