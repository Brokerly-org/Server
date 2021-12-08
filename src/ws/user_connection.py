from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)

from core.schemas.user import User
from core.models.connections_manager import get_connection_manager
from api.users import get_user_by_token, send_message


ws_user_connect_endpoint = APIRouter()


@ws_user_connect_endpoint.websocket("/user_connect")
async def connect_user_ws(ws: WebSocket, user: User = Depends(get_user_by_token)):
    connection_manager = get_connection_manager()
    session_id = str(uuid4())

    await ws.accept()
    await connection_manager.register_user_connection(ws, user.token, session_id)

    try:
        while True:
            data = await ws.receive_json()
            message = data["message"]
            botname = data["botname"]
            send_message(user, botname, message)
    except (WebSocketDisconnect, KeyError):
        connection_manager.unregister_user_connection(session_id=session_id)
