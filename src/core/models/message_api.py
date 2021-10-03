from typing import Callable
from collections import defaultdict
from uuid import UUID

from core.models.database import DB
from core.models.orm.chat import ChatModel
from core.models.orm.message import MessageModel
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
        self.callback_data = {}

        self.__class__._instance = self

    async def _notify_listeners(self, token: str, data: dict = None):
        callbacks = self.listeners[token].values()
        for callback in callbacks:
            await callback(data)

    async def bot_push(self, bot: Bot, chat_id: str, message: InputMessage):
        chat = await ChatModel.load_by_id(chat_id)
        if chat is None:
            raise KeyError
        if chat.botname != bot.botname:
            raise KeyError
        await MessageModel.create(chat.id, chat.size, "bot", message)
        await self._notify_listeners(chat.user_token)

    async def user_push(self, user: User, botname: str, message: str):
        chat = await ChatModel.load_by_botname_and_user_token(botname, user.token)
        if chat is None:
            raise KeyError  # TODO: replace with costume exception
        message = InputMessage(text=message)
        await MessageModel.create(chat.id, chat.size, "user", message)
        await self._notify_listeners(botname)

    async def user_push_callback(self, user: User, botname: str, data: dict):
        chat = await ChatModel.load_by_botname_and_user_token(botname, user.token)
        if chat is None:
            raise KeyError  # TODO: replace with costume exception
        data = {"chat_id": chat.id, "data": data}
        await self._notify_listeners(botname, data)

    async def bot_push_callback(self, bot: Bot, chat_id: str, data: dict):
        chat = await ChatModel.load_by_id(chat_id)
        if chat is None:
            raise KeyError
        if chat.botname != bot.botname:
            raise KeyError
        data = {"chat_id": chat.id, "data": data}
        await self._notify_listeners(chat.user_token, data)

    def listen_on(self, token: str, callback: Callable, session_id: UUID):
        self.listeners[token][session_id] = callback

    def remove_listener(self, token: str, session_id: UUID):
        del self.listeners[token][session_id]
