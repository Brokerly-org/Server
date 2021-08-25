from fastapi import HTTPException, status

from core.schemas.user import User
from core.schemas.bot import Bot
from core.models.orm.bot import BotModel
from core.models.orm.user import UserModel


async def validate_user_token(token: str) -> User:
    user = await UserModel.load_by_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token"
        )
    return user


async def validate_user_is_owner_of_bot(user: User, bot: Bot):
    if bot is None or bot.owner_token != user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permissions to delete this bot",
        )


async def validate_bot_token(token: str) -> Bot:
    bot = await BotModel.load_by_token(token)
    if bot is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bot token"
        )
    return bot
