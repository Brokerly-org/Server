from uuid import UUID

from fastapi import WebSocket


from core.models.message_api import MessageApi
from core.models.orm import load_user_by_token, load_bot_by_bot_name, get_user_unread_messages, get_bot_unread_messages


class ConnectionManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("ConnectionManager not initialize")
        return cls._instance

    def __init__(self, data_api: MessageApi):
        self.data_api = data_api
        self.connections = {}

        self.__class__._instance = self

    async def callback(self, identifier: str):
        # identifier == user token or botname
        ws: WebSocket = self.connections.get(identifier)
        if ws is None:
            return
        user = await load_user_by_token(identifier)
        if user is not None:
            user_messages = await get_user_unread_messages(identifier)
            await ws.send_json(user_messages)
        else:
            bot = await load_bot_by_bot_name(identifier)
            bot_messages = await get_bot_unread_messages(bot.botname)
            await ws.send_json(bot_messages)

    async def _register_listener(self, token: str, session_id: UUID):
        self.data_api.listen_on(token, lambda: self.callback(token), session_id)
        await self.callback(token)

    async def register_connection(self, ws: WebSocket, token: str, session_id: UUID):
        self.connections[token] = ws
        await self._register_listener(token, session_id)

    def unregister_connection(self, token: str, session_id: UUID):
        del self.connections[token]
        self.data_api.remove_listener(token, session_id)
