from time import time
from collections import defaultdict

from db import DB
from models import Bot, Message


async def update_bot_last_online(botname: str):
    db: DB = DB.get_instance()
    # TODO: utc time
    await db.update_bot_last_online(botname, time())


async def get_bot_by_token(bot_token: str) -> Bot:
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
        last_online=bot_data[5],
    )
    return bot


async def get_bot_unread_messages(botname: str):
    db: DB = DB.get_instance()
    messages_data = await db.get_bot_unread_messages(botname)
    chats = defaultdict(list)
    for message in messages_data:
        message = Message(
            content=message[0],
            index=message[1],
            sender=message[2],
            created_at=message[3],
            chat_id=message[4],
            read_status=False,
        )
        chats[message.chat_id].append(message.dict())
        await db.mark_message_as_read(message.index, message.chat_id)
    messages = [{"chat": chat_id, "messages": messages} for chat_id, messages in chats.items()]
    return messages
