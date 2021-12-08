from functools import lru_cache

from fastapi import WebSocket

from events import listen_on, StopListening
from api.users import get_unread_messages as get_user_unread_messages, get_user_by_token
from api.bots import get_unread_messages as get_bot_unread_messages, get_bot_by_botname, update_bot_online_status


class ConnectionManager:
    def __init__(self):
        self.sessions = {}

    def listen_on_user_token(self, user_token: str, session_id: str):
        @listen_on(user_token)
        async def handler_user_message():
            ws = self.sessions.get(session_id, None)
            if ws is None:
                raise StopListening
            messages = get_user_unread_messages(get_user_by_token(user_token))
            await ws.send_json(messages)

    def listen_on_bot_botname(self, botname: str, session_id: str):
        @listen_on(botname)
        async def handler_user_message():
            ws = self.sessions.get(session_id, None)
            if ws is None:
                raise StopListening
            messages = get_bot_unread_messages(get_bot_by_botname(botname))
            await ws.send_json(messages)

    def register_user_connection(self, ws: WebSocket, user_token: str, session_id: str):
        self.sessions[session_id] = ws
        self.listen_on_user_token(user_token, session_id)

    def register_bot_connection(self, ws: WebSocket, botname: str, session_id: str):
        self.sessions[session_id] = ws
        self.listen_on_bot_botname(botname, session_id)
        update_bot_online_status(botname, True)

    def unregister_bot_connection(self, botname: str, session_id: str):
        del self.sessions[session_id]
        update_bot_online_status(botname, False)
        print(f"WS Connection Closed [{session_id}]")

    def unregister_user_connection(self, session_id: str):
        del self.sessions[session_id]
        print(f"WS Connection Closed [{session_id}]")


@lru_cache
def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()
