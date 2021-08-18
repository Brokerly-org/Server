from uuid import UUID

from fastapi import WebSocket

from db import DB
from data_api import DataApi


class ConnectionManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("ConnectionManager not initialize")
        return cls._instance

    def __init__(self, data_api: DataApi):
        self.db: DB = DB.get_instance()
        self.data_api = data_api
        self.connections = {}

        self.__class__._instance = self

    async def callback(self, token: str):
        ws: WebSocket = self.connections.get(token)
        if ws is None:
            return
        user = await self.db.get_user(token)
        if user is not None:
            await ws.send_json(user.pull_from_chats())
        else:
            bot = await self.db.get_bot_by_token(token)
            await ws.send_json(bot.pull_from_chats())

    async def _register_listener(self, token: str, session_id: UUID):
        self.data_api.listen_on(token, lambda: self.callback(token), session_id)
        await self.callback(token)

    async def register_connection(self, ws: WebSocket, token: str, session_id: UUID):
        self.connections[token] = ws
        await self._register_listener(token, session_id)

    def unregister_connection(self, token: str, session_id: UUID):
        del self.connections[token]
        self.data_api.remove_listener(token, session_id)

