from fastapi import APIRouter, Depends, HTTPException, status

from core.schemas.bot import Bot
from core.schemas.message import InputMessage
from core.models.message_api import MessageApi

from ..validators import validate_bot_token

bot_push_endpoint = APIRouter(tags=["bot"])


@bot_push_endpoint.post("/push")
async def push_message_as_bot(chat_id: str, message: InputMessage, bot: Bot = Depends(validate_bot_token)):
    data_api: MessageApi = MessageApi.get_instance()
    try:
        await data_api.bot_push(bot, chat_id, message)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat Id not found"
        )
    return {"sent": True}
