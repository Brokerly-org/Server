from fastapi import APIRouter, Depends, HTTPException, status

from core.schemas.bot import Bot
from core.models.message_api import MessageApi

from ..validators import validate_bot_token

bot_callback_push_endpoint = APIRouter(tags=["bot"])


@bot_callback_push_endpoint.post("/callback")
async def push_callback_as_bot(chat_id: str, data: dict, bot: Bot = Depends(validate_bot_token)):
    data_api: MessageApi = MessageApi.get_instance()
    try:
        await data_api.bot_push_callback(bot, chat_id, data)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat Id not found"
        )
    return {"sent": True}
