from fastapi import APIRouter, Depends

from core.models.orm import create_bot
from ..validators import validate_user_token


create_bot_endpoint = APIRouter(tags=["admin"])


@create_bot_endpoint.put("/create_bot")
async def create_bot_route(
    botname: str, title: str, description: str, user=Depends(validate_user_token)
):
    new_bot_token = await create_bot(user.token, botname, title, description)
    return {"bot_token": new_bot_token}
