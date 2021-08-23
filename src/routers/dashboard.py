from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

dashboard_router = APIRouter()

dashboard_router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# svelte spa
@dashboard_router.get("/")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


for route in ("login", "register", "dashboard"):

    @dashboard_router.get(f"/{route}")
    async def serve_spa(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

