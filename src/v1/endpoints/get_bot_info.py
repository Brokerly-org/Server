from fastapi import APIRouter, HTTPException, status

from core.models.orm.bot import BotModel

get_bot_info_endpoint = APIRouter(tags=["user"])


@get_bot_info_endpoint.get("/bot_info")
async def bot_info(botname: str):
    bot = await BotModel.load_by_botname(botname)
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found."
        )
    return bot.dict(include={"title", "botname", "description", "online_status"})
