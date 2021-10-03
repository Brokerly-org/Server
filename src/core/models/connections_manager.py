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

    async def user_callback(self, user_token: str, data: dict = None):
        ws: WebSocket = self.connections.get(user_token)
        if ws is None:
            return
        user_messages = await UserModel.get_unread_messages(user_token)
        await ws.send_json(user_messages)
        if data:
            await ws.send_json(data)

    async def bot_callback(self, botname: str, data: dict = None):
        ws: WebSocket = self.connections.get(botname)
        if ws is None:
            return
        bot = await BotModel.load_by_botname(botname)
        bot_messages = await BotModel.get_unread_messages(bot.botname)
        await ws.send_json(bot_messages)
        if data:
            await ws.send_json(data)

    async def _register_listener(self, identifier: str, session_id: UUID, is_bot: bool):
        if is_bot:
            self.data_api.listen_on(identifier, lambda data: self.bot_callback(identifier, data), session_id)
            await self.bot_callback(identifier)
        else:
            self.data_api.listen_on(identifier, lambda data: self.user_callback(identifier, data), session_id)
            await self.user_callback(identifier)

    async def register_user_connection(self, ws: WebSocket, user_token: str, session_id: UUID):
        self.connections[user_token] = ws
        await self._register_listener(user_token, session_id, is_bot=False)

    async def register_bot_connection(self, ws: WebSocket, botname: str, session_id: UUID):
        self.connections[botname] = ws
        await self._register_listener(botname, session_id, is_bot=True)
        await BotModel.update_online_status(botname=botname, is_online=True)

    async def unregister_bot_connection(self, botname: str, session_id: UUID):
        del self.connections[botname]
        self.data_api.remove_listener(botname, session_id)
        await BotModel.update_online_status(botname=botname, is_online=False)
        print(f"WS Connection Closed [{session_id}]")

    async def unregister_user_connection(self, user_token: str, session_id: UUID):
        del self.connections[user_token]
        self.data_api.remove_listener(user_token, session_id)
        print(f"WS Connection Closed [{session_id}]")
