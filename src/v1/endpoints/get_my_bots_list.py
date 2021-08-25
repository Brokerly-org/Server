from fastapi import APIRouter, Depends

from core.models.orm.user import UserModel
from ..validators import validate_user_token


get_my_bots_endpoint = APIRouter(tags=["admin"])


@get_my_bots_endpoint.get("/bot_list")
async def bot_list(user=Depends(validate_user_token)):
    bots_list = []
    bots_objects = await UserModel.get_bot_list(user_token=user.token)
    for bot in bots_objects:
        bots_list.append(bot.dict(exclude={"owner_token", "chats"}))
    return {"bots": bots_list}
