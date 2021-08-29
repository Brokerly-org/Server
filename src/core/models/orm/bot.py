from typing import Union
from secrets import token_urlsafe
from collections import defaultdict

from core.models.database import DB
from core.models.orm.message import MessageModel
from core.schemas.bot import Bot


__all__ = ["BotModel"]


class BotModel:
    @classmethod
    async def create(
            cls, user_token: str, botname: str, title: str, description: str
    ) -> str:
        db: DB = DB.get_instance()
        token = token_urlsafe(15)
        await db.create_bot(token, botname, title, description, user_token, online_status=False)
        return token

    @classmethod
    async def delete(cls, botname: str):
        db: DB = DB.get_instance()
        await db.delete_bot(botname)
        return True

    @classmethod
    async def get_unread_messages(cls, botname: str):
        db: DB = DB.get_instance()
        messages_data = await db.get_bot_unread_messages(botname)
        chats = defaultdict(list)
        for raw_message in messages_data:
            message = await MessageModel.load_from_raw(raw_message)
            await MessageModel.mark_as_read(message.index, message.chat_id)
            chats[message.chat_id].append(message.dict())
        messages = [
            {"chat": chat_id, "messages": messages} for chat_id, messages in chats.items()
        ]
        return messages

    # @classmethod
    # async def update_last_online(cls, botname: str, new_time):
    #     db: DB = DB.get_instance()
    #     await db.update_bot_last_online(botname, new_time)

    @classmethod
    async def update_online_status(cls, botname: str, is_online: bool):
        db: DB = DB.get_instance()
        await db.update_bot_online_status(botname, is_online)

    @classmethod
    async def load_by_botname(cls, botname: str) -> Union[Bot, None]:
        db: DB = DB.get_instance()
        bot_data = await db.get_bot_by_bot_name(botname)
        if bot_data is None:
            return
        bot = Bot(
            token=bot_data[0],
            botname=bot_data[1],
            title=bot_data[2],
            description=bot_data[3],
            owner_token=bot_data[4],
            online_status=bot_data[5],
        )
        return bot

    @classmethod
    async def load_by_token(cls, bot_token: str) -> Union[Bot, None]:
        db: DB = DB.get_instance()
        bot_data = await db.get_bot_by_token(bot_token)
        if not bot_data:
            return
        bot = Bot(
            token=bot_data[0],
            botname=bot_data[1],
            title=bot_data[2],
            description=bot_data[3],
            owner_token=bot_data[4],
            online_status=bot_data[5],
        )
        return bot

    @classmethod
    async def load_from_raw(cls, raw_bot: list) -> Bot:
        bot = Bot(
            token=raw_bot[0],
            botname=raw_bot[1],
            title=raw_bot[2],
            description=raw_bot[3],
            owner_token=raw_bot[4],
            online_status=raw_bot[5],
        )
        return bot
