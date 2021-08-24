from fastapi import APIRouter, Depends, HTTPException, status


from core.models.message_api import MessageApi
from core.models.orm import create_chat, load_bot_by_bot_name

from ..validators import validate_user_token

user_push_endpoint = APIRouter(tags=["user"])


@user_push_endpoint.post("/push")
async def push_message_to_bot(message: str, botname: str, user=Depends(validate_user_token)):
    data_api: MessageApi = MessageApi.get_instance()
    bot = await load_bot_by_bot_name(botname)
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="botname not found"
        )
    try:
        await data_api.user_push(user, botname, message)
    except KeyError:
        await create_chat(user.token, botname)
        await data_api.user_push(user, botname, message)
