from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends, WebSocket, WebSocketDisconnect

from db import DB
from models import User
from data_api import DataApi
from .connections_manager import ConnectionManager


user_websocket_route = APIRouter()


async def get_user(token: str) -> User:
    db: DB = DB.get_instance()
    user = await db.get_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user


@user_websocket_route.websocket("/user_ws/connect")
async def connect_bot_ws(ws: WebSocket, user: User = Depends(get_user)):
    data_api: DataApi = DataApi.get_instance()
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
        connection_manager.unregister_connection(token=user.token, session_id=session_id)
