from fastapi import APIRouter, Depends

from core.models.orm.user import UserModel

from ..validators import validate_user_token


get_bots_status_endpoint = APIRouter(tags=["user"])


@get_bots_status_endpoint.get("/bots_status")
async def get_bots_status(user=Depends(validate_user_token)):
    bots = await UserModel.get_bots_online_status(user.token)
    return bots
