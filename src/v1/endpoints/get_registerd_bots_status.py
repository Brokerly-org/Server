from fastapi import APIRouter, Depends

from core.models.orm import get_bots_last_online

from ..validators import validate_user_token


get_bots_status_endpoint = APIRouter(tags=["user"])


@get_bots_status_endpoint.get("/bots_status")
async def get_bots_status(user=Depends(validate_user_token)):
    bots = await get_bots_last_online(user.token)
    return bots
