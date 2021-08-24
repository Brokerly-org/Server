from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core.settings import Settings


dashboard_router = APIRouter()
settings = Settings()

print(str(settings.dashboard_templates_path))
templates = Jinja2Templates(directory=str(settings.dashboard_templates_path))


for route in settings.dashboard_routes:
    @dashboard_router.get(route)
    async def serve_spa(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
