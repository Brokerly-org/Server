from time import time

from fastapi import APIRouter, Depends

from core.models.orm import update_bot_last_online, get_bot_unread_messages
from core.schemas.bot import Bot

from ..validators import validate_bot_token

bot_pull_endpoint = APIRouter(tags=["bot"])


@bot_pull_endpoint.get("/pull")
async def pull_messages_as_bot(bot: Bot = Depends(validate_bot_token)):
    messages = await get_bot_unread_messages(botname=bot.botname)
    await update_bot_last_online(bot.botname, time())
    return {"chats": messages}

