from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect

from db import DB
from models import Bot
from data_api import DataApi
from .connections_manager import ConnectionManager


bot_websocket_route = APIRouter()


async def get_bot(token: str) -> Bot:
    db: DB = DB.get_instance()
    bot = await db.get_bot_by_token(token)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return bot


@bot_websocket_route.websocket("/bot_ws/connect")
async def connect_bot_ws(ws: WebSocket, bot: Bot = Depends(get_bot)):
    data_api: DataApi = DataApi.get_instance()
    connection_manager: ConnectionManager = ConnectionManager.get_instance()
    session_id = uuid4()

    await ws.accept()
    await connection_manager.register_connection(ws, bot.token, session_id)

    try:
        while True:
            data = await ws.receive_json()
            message = data["message"]
            chat_id = data["chat_id"]
            await data_api.bot_push(bot, chat_id, message)
    except WebSocketDisconnect:
        connection_manager.unregister_connection(token=bot.token, session_id=session_id)
