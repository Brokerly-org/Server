from fastapi import APIRouter, Depends, HTTPException, status

from core.models.orm import load_bot_by_bot_name, delete_bot
from core.schemas.user import User
from ..validators import validate_user_token, validate_user_is_owner_of_bot


delete_bot_endpoint = APIRouter(tags=["admin"])


@delete_bot_endpoint.delete("/delete_bot")
async def delete_bot_route(botname: str, user: User = Depends(validate_user_token)):
    bot = await load_bot_by_bot_name(botname)
    await validate_user_is_owner_of_bot(user, bot)
    deleted = await delete_bot(botname)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found"
        )
    return {"deleted": deleted}
