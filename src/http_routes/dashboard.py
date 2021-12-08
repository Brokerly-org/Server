from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.settings import get_settings

__all__ = ["dashboard_router"]


settings = get_settings()
dashboard_router = APIRouter()

templates = Jinja2Templates(directory=str(settings.dashboard_templates_path))


for route in settings.dashboard_routes:
    @dashboard_router.get(route)
    async def serve_spa(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
