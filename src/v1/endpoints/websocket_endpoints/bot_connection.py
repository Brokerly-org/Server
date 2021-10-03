from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)


from core.models.connections_manager import ConnectionManager
from core.schemas.bot import Bot
from core.schemas.message import InputMessage
from core.models.message_api import MessageApi

from ...validators import validate_bot_token


ws_bot_connect_endpoint = APIRouter()


@ws_bot_connect_endpoint.websocket("/bot_connect")
async def connect_bot_ws(ws: WebSocket, bot: Bot = Depends(validate_bot_token)):
    data_api: MessageApi = MessageApi.get_instance()
    connection_manager: ConnectionManager = ConnectionManager.get_instance()
    session_id = uuid4()

    await ws.accept()
    await connection_manager.register_bot_connection(ws, bot.botname, session_id)

    try:
        while True:
            data = await ws.receive_json()
            message = InputMessage(**data["message"])
            chat_id = data["chat_id"]
            await data_api.bot_push(bot, chat_id, message)
    except (WebSocketDisconnect, KeyError):
        await connection_manager.unregister_bot_connection(bot.botname, session_id=session_id)

