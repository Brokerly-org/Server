from typing import Union
from collections import defaultdict
from secrets import token_urlsafe

from core.models.database import DB
from core.models.orm.message import MessageModel
from core.models.orm.bot import BotModel

from core.schemas.user import User


__all__ = ["UserModel"]


class UserModel:
    @classmethod
    async def create(cls, name: str, email: str, password_hash: str) -> str:
        db: DB = DB.get_instance()
        token = token_urlsafe(15)
        await db.create_user(token, name, email, password_hash)
        return token

    @classmethod
    async def try_login(cls, email: str, password_hash: str) -> Union[str, None]:
        db: DB = DB.get_instance()
        user_token = await db.find_user_by_email_and_password(email, password_hash)
        if user_token is None:
            return
        return user_token

    @classmethod
    async def get_updates_count(cls, user_token: str) -> int:
        db: DB = DB.get_instance()
        return await db.get_user_unread_messages_count(user_token)

    @classmethod
    async def get_bots_online_status(cls, user_token: str) -> list:
        db: DB = DB.get_instance()
        bots_status = await db.get_bots_status(user_token)
        bots = []
        for bot in bots_status:
            bots.append({"botname": bot[1], "online_status": bot[0]})
        return bots

    @classmethod
    async def get_bot_list(cls, user_token: str) -> list:
        db: DB = DB.get_instance()
        bot_list_data = await db.get_bot_list(user_token)
        bots = []
        for raw_bot in bot_list_data:
            bot = await BotModel.load_from_raw(raw_bot)
            bots.append(bot)
        return bots

    @classmethod
    async def get_unread_messages(cls,  user_token: str) -> list:
        db: DB = DB.get_instance()
        messages_data = await db.get_user_unread_messages(user_token)
        chats = defaultdict(list)
        for raw_message in messages_data:
            botname = raw_message[6]
            message = await MessageModel.load_from_raw(raw_message)
            await MessageModel.mark_as_read(message.index, message.chat_id)
            chats[botname].append(message.dict(exclude={"chat_id", "read_status"}))
        messages = [
            {"chat": botname, "messages": messages} for botname, messages in chats.items()
        ]
        return messages

    @classmethod
    async def load_by_token(cls, user_token: str) -> Union[User, None]:
        db: DB = DB.get_instance()
        user_data = await db.get_user(user_token)
        if not user_data:
            return
        user = User(
            token=user_data[0],
            name=user_data[1],
            email=user_data[2],
            password_hash=user_data[3],
        )
        return user
