from fastapi import APIRouter, Depends, HTTPException, status

from models import Bot
from data_api import DataApi
from data_layer.bot import (
    get_bot_by_token,
    get_bot_unread_messages,
    update_bot_last_online,
)

bot_router = APIRouter(prefix="/bot", tags=["bot"])


async def get_bot(token: str) -> Bot:
    bot = await get_bot_by_token(token)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bot token")
    return bot


@bot_router.get("/pull")
async def pull_messages_as_bot(bot: Bot = Depends(get_bot)):
    messages = await get_bot_unread_messages(botname=bot.botname)
    await update_bot_last_online(bot.botname)
    return {"chats": messages}


@bot_router.post("/push")
async def push_message_as_bot(chat_id: str, message: str, bot: Bot = Depends(get_bot)):
    data_api: DataApi = DataApi.get_instance()
    try:
        await data_api.bot_push(bot, chat_id, message)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat Id not found")
    return
