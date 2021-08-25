from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)

from core.models.message_api import MessageApi
from core.schemas.user import User

from ...validators import validate_user_token

from core.models.connections_manager import ConnectionManager


ws_user_connect_endpoint = APIRouter()


@ws_user_connect_endpoint.websocket("/user_connect")
async def connect_user_ws(ws: WebSocket, user: User = Depends(validate_user_token)):
    data_api: MessageApi = MessageApi.get_instance()
    connection_manager: ConnectionManager = ConnectionManager.get_instance()
    session_id = uuid4()

    await ws.accept()
    await connection_manager.register_connection(ws, user.token, session_id)

    try:
        while True:
            data = await ws.receive_json()
            message = data["message"]
            chat_id = data["chat_id"]
            await data_api.user_push(user, chat_id, message)
    except WebSocketDisconnect:
        connection_manager.unregister_connection(
            identifier=user.token, session_id=session_id
        )
