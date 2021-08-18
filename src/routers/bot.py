from fastapi import APIRouter, Depends, HTTPException, status

from models import Bot
from db import DB
from data_api import DataApi
from time import time

bot_router = APIRouter(prefix="/bot", tags=["bot"])


async def get_bot(token: str) -> Bot:
    db: DB = DB.get_instance()
    bot = await db.get_bot_by_token(token)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bot token")
    return bot


@bot_router.get("/pull")
async def pull_messages_as_bot(bot: Bot = Depends(get_bot)):
    db: DB = DB.get_instance()
    # messages = bot.pull_from_chats()
    messages = await db.get_bot_unread_messages(botname=bot.botname)
    new_time = time()
    bot.last_online = new_time
    await db.update_bot_last_online(bot.botname, new_time)
    return {"chats": messages}


@bot_router.post("/push")
async def push_message_as_bot(chat_id: str, message: str, bot: Bot = Depends(get_bot)):
    data_api: DataApi = DataApi.get_instance()
    try:
        await data_api.bot_push(bot, chat_id, message)
        # bot.push_to_chat(chat_id, message)
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat Id not found")
    return
