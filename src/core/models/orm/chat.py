from typing import Union
from secrets import token_urlsafe

from core.models.database import DB
from core.schemas.chat import Chat


__all__ = ["ChatModel"]


class ChatModel:
    @classmethod
    async def create(cls, user_token: str, botname: str) -> str:
        db: DB = DB.get_instance()
        chat_id = token_urlsafe(15)
        await db.create_chat(chat_id, botname, user_token, True, 0)
        return chat_id

    @classmethod
    async def load_by_id(cls, chat_id: str) -> Union[Chat, None]:
        db: DB = DB.get_instance()
        chat_data = await db.get_chat_by_id(chat_id)
        if not chat_data:
            return
        chat = Chat(
            id=chat_data[0],
            botname=chat_data[1],
            user_token=chat_data[2],
            active=chat_data[3],
            size=chat_data[4],
        )
        return chat

    @classmethod
    async def load_by_botname_and_user_token(cls, botname: str, user_token: str) -> Union[Chat, None]:
        db: DB = DB.get_instance()
        chat_data = await db.get_chat(user_token, botname)
        if not chat_data:
            return
        chat = Chat(
            id=chat_data[0],
            botname=chat_data[1],
            user_token=chat_data[2],
            active=chat_data[3],
            size=chat_data[4],
        )
        return chat
