from uuid import UUID

from fastapi import WebSocket


from core.models.message_api import MessageApi
from core.models.orm.bot import BotModel
from core.models.orm.user import UserModel


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
        user = await UserModel.load_by_token(identifier)
        if user is not None:
            user_messages = await UserModel.get_unread_messages(identifier)
            await ws.send_json(user_messages)
        else:
            bot = await BotModel.load_by_botname(identifier)
            bot_messages = await BotModel.get_unread_messages(bot.botname)
            await ws.send_json(bot_messages)

    async def _register_listener(self, identifier: str, session_id: UUID):
        self.data_api.listen_on(identifier, lambda: self.callback(identifier), session_id)
        await self.callback(identifier)

    async def register_connection(self, ws: WebSocket, identifier: str, session_id: UUID):
        self.connections[identifier] = ws
        await self._register_listener(identifier, session_id)

    def unregister_connection(self, identifier: str, session_id: UUID):
        del self.connections[identifier]
        self.data_api.remove_listener(identifier, session_id)
