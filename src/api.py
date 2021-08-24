from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from core.models.database import DB
from core.models.message_api import MessageApi
from core.models.connections_manager import ConnectionManager

from v1 import user_router, bot_router, auth_router, admin_router, ws_router, dashboard_router


app = FastAPI(title="Brokerly")
app.mount("/static", StaticFiles(directory="core/views/static"), name="static")


app.include_router(auth_router)
app.include_router(bot_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(ws_router)
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
