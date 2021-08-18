from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# for client side serving
from routers.bot import bot_router
from routers.user import user_router
from db import DB
from data_api import DataApi
from websockets_routes import ConnectionManager, user_websocket_route, bot_websocket_route


app = FastAPI(title="Brokerly")


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Allow CORS, TODO change to real origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot_router)
app.include_router(user_router)
app.include_router(bot_websocket_route)
app.include_router(user_websocket_route)


# svelte spa
@app.get("/")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

for route in ('login', 'register', 'dashboard'):
    @app.get(f'/{route}')
    async def serve_spa(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

# TODO route all spa
# @app.get("/{rest_of_path:path}")
# async def serve_spa_all(request: Request, rest_of_path: str):
#     return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup():
    import aiosqlite
    # Initialize
    db = DB()
    # for testing..
    try:
        await db.create_tables()
    except aiosqlite.OperationalError:
        pass
    else:
        await db.create_admin_user()

    data_api = DataApi()
    ConnectionManager(data_api)


@app.on_event("shutdown")
async def shutdown():
    db: DB = DB.get_instance()
    db.close()

