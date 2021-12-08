from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)


from core.models.connections_manager import get_connection_manager
from core.schemas.bot import Bot
from core.schemas.message import InputMessage
from api.bots import get_bot_by_token, send_message


ws_bot_connect_endpoint = APIRouter()


@ws_bot_connect_endpoint.websocket("/bot_connect")
async def connect_bot_ws(ws: WebSocket, bot: Bot = Depends(get_bot_by_token)):
    connection_manager = get_connection_manager()
    session_id = str(uuid4())

    await ws.accept()
    await connection_manager.register_bot_connection(ws, bot.botname, session_id)

    try:
        while True:
            data = await ws.receive_json()
            message = InputMessage(**data["message"])
            chat_id = data["chat_id"]
            send_message(bot, message.text, chat_id)
    except (WebSocketDisconnect, KeyError):
        connection_manager.unregister_bot_connection(bot.botname, session_id=session_id)

