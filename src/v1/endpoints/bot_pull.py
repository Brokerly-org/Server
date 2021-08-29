from fastapi import APIRouter, Depends

from core.models.orm.bot import BotModel
from core.schemas.bot import Bot

from ..validators import validate_bot_token

bot_pull_endpoint = APIRouter(tags=["bot"])


@bot_pull_endpoint.get("/pull")
async def pull_messages_as_bot(bot: Bot = Depends(validate_bot_token)):
    messages = await BotModel.get_unread_messages(botname=bot.botname)
    return {"chats": messages}

