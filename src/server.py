from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from core.settings import get_settings
from core.models.database import get_db_engine

from http_routes import user_router, bot_router, admin_router, dashboard_router


settings = get_settings()
app = FastAPI(title="Brokerly")
app.mount("/static", StaticFiles(directory=str(settings.dashboard_static_path)), name="static")


app.include_router(bot_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(dashboard_router)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(get_db_engine())


@app.on_event("shutdown")
async def shutdown():
    get_db_engine().dispose()
