"""WebSocket interface for the server"""
from fastapi import APIRouter

from .user_connection import ws_user_connect_endpoint
from .bot_connection import ws_bot_connect_endpoint

__all__ = ["ws_router"]


ws_router = APIRouter(prefix="/ws")
ws_router.include_router(ws_user_connect_endpoint)
ws_router.include_router(ws_bot_connect_endpoint)
