from .bots import bot_router
from .admins import admin_router
from .users import user_router
from .dashboard import dashboard_router


__all__ = ["bot_router", "admin_router", "user_router", "dashboard_router"]
