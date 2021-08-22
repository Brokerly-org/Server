from fastapi import APIRouter, Depends, HTTPException, status

from models import User
from data_layer.user import (
    get_user as get_user_by_token,
    get_bot_by_bot_name,
)
from data_layer.admin import (
    create_bot,
    delete_bot,
    get_bot_list,
)


admin_router = APIRouter(prefix="/admin", tags=["admin"])


async def get_user(token: str) -> User:
    user = await get_user_by_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token"
        )
    return user


@admin_router.put("/create_bot")
async def create_bot_route(
    botname: str, title: str, description: str, user=Depends(get_user)
):
    new_bot_token = await create_bot(user.token, botname, title, description)
    return {"bot_token": new_bot_token}


@admin_router.delete("/delete_bot")
async def delete_bot_route(botname: str, user: User = Depends(get_user)):
    bot = await get_bot_by_bot_name(botname)
    if bot is None or bot.owner_token != user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permissions to delete this bot",
        )
    deleted = await delete_bot(botname)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found"
        )
    return {"deleted": deleted}


@admin_router.get("/bot_list")
async def bot_list(user=Depends(get_user)):
    bots_list = []
    bots_objects = await get_bot_list(user_token=user.token)
    for bot in bots_objects:
        bots_list.append(bot.dict(exclude={"owner_token", "chats"}))
    return {"bots": bots_list}
