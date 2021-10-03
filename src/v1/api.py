from fastapi import APIRouter

from .endpoints.delete_bot import delete_bot_endpoint
from .endpoints.create_bot import create_bot_endpoint
from .endpoints.get_my_bots_list import get_my_bots_endpoint

from .endpoints.bot_push import bot_push_endpoint
from .endpoints.bot_callback_push import bot_callback_push_endpoint
from .endpoints.bot_pull import bot_pull_endpoint

from .endpoints.user_push import user_push_endpoint
from .endpoints.user_callback_push import user_callback_push_endpoint
from .endpoints.user_pull import user_pull_endpoint

from .endpoints.get_bot_info import get_bot_info_endpoint
from .endpoints.get_registerd_bots_status import get_bots_status_endpoint
from .endpoints.has_updates import has_updates_endpoint

from .endpoints.login import login_endpoint
from .endpoints.register import register_endpoint

from .endpoints.websocket_endpoints.user_connection import ws_user_connect_endpoint
from .endpoints.websocket_endpoints.bot_connection import ws_bot_connect_endpoint

from .endpoints.dashboard.api import dashboard_router


__all__ = ["user_router", "bot_router", "auth_router", "admin_router", "ws_router", "dashboard_router"]

user_router = APIRouter(prefix="/user")
user_router.include_router(user_pull_endpoint)
user_router.include_router(user_push_endpoint)
user_router.include_router(get_bot_info_endpoint)
user_router.include_router(get_bots_status_endpoint)
user_router.include_router(has_updates_endpoint)
user_router.include_router(user_callback_push_endpoint)

auth_router = APIRouter(prefix="/auth")
auth_router.include_router(login_endpoint)
auth_router.include_router(register_endpoint)

bot_router = APIRouter(prefix="/bot")
bot_router.include_router(bot_pull_endpoint)
bot_router.include_router(bot_push_endpoint)
bot_router.include_router(bot_callback_push_endpoint)

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(create_bot_endpoint)
admin_router.include_router(delete_bot_endpoint)
admin_router.include_router(get_my_bots_endpoint)

ws_router = APIRouter()
ws_router.include_router(ws_bot_connect_endpoint)
ws_router.include_router(ws_user_connect_endpoint)
