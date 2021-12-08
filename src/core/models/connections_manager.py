from functools import lru_cache
from uuid import UUID

from fastapi import WebSocket
from sqlmodel import Session, select

from events import listen_on, StopListening
from core.models.database import get_db_engine
from core.schemas.bot import Bot


def update_bot_online_status(botname: str, change_to: bool):
    with Session(get_db_engine()) as db_session:
        get_bot_query = select(Bot).where(Bot.botname == botname)
        bot = db_session.exec(get_bot_query).one_or_none()
        if bot is None:
            return
        bot.online_status = change_to
        db_session.add(bot)
        db_session.commit()


class ConnectionManager:
    def __init__(self):
        self.sessions = {}

    def listen_on_user_token(self, user_token: str, session_id: str):
        @listen_on(user_token)
        async def handler_user_message(message: dict):
            ws = self.sessions.get(session_id, None)
            if ws is None:
                raise StopListening
            await ws.send_json(message)

    def listen_on_bot_botname(self, botname: str, session_id: str):
        @listen_on(botname)
        async def handler_user_message(message: dict):
            ws = self.sessions.get(session_id, None)
            if ws is None:
                raise StopListening
            await ws.send_json(message)

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
