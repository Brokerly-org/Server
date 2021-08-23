from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# for client side serving
from routers.dashboard import dashboard_router
from routers.bot import bot_router
from routers.user import user_router
from routers.admin import admin_router
from routers.auth import auth_router
from db import DB
from message_api import MessageApi
from websockets_routes import (
    ConnectionManager,
    user_websocket_route,
    bot_websocket_route,
)


app = FastAPI(title="Brokerly")
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth_router)
app.include_router(bot_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(bot_websocket_route)
app.include_router(user_websocket_route)
app.include_router(dashboard_router)


@app.on_event("startup")
async def startup():
    import aiosqlite

    # Initialize
    db = DB()
    try:
        await db.create_tables()
    except aiosqlite.OperationalError:
        pass
    else:
        # for testing
        await db.create_admin_user()

    data_api = MessageApi()
    ConnectionManager(data_api)


@app.on_event("shutdown")
async def shutdown():
    db: DB = DB.get_instance()
    db.close()
