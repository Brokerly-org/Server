from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status


from core.models.message_api import MessageApi
from core.models.orm.bot import BotModel

from ..validators import validate_user_token

user_callback_push_endpoint = APIRouter(tags=["user"])


@user_callback_push_endpoint.post("/callback")
async def push_callback_to_bot(widget: str, value: Any, botname: str, user=Depends(validate_user_token)):
    data = {widget: value}
    data_api: MessageApi = MessageApi.get_instance()
    bot = await BotModel.load_by_botname(botname)
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="botname not found"
        )
    try:
        await data_api.user_push_callback(user, botname, data)
    except KeyError:
        raise
