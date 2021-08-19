from secrets import token_urlsafe
from collections import defaultdict

from models import User, Message, Chat, Bot
from db import DB


async def create_user(name: str, email: str, password_hash: str) -> str:
    db: DB = DB.get_instance()
    token = token_urlsafe(15)
    new_user = User(token=token, name=name, email=email, password_hash=password_hash)
    await db.create_user(new_user)
    return token


async def get_user(user_token: str) -> User:
    db: DB = DB.get_instance()
    user_data = await db.get_user(user_token)
    if not user_data:
        return
    user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
    return user


async def get_user_unread_messages(user_token: str):
    db: DB = DB.get_instance()
    messages_data = await db.get_user_unread_messages(user_token)
    chats = defaultdict(list)
    for message in messages_data:
        botname = message[5]
        message = Message(
            content=message[0],
            index=message[1],
            sender=message[2],
            created_at=message[3],
            chat_id=message[4],
            read_status=False,
        )
        chats[botname].append(message.dict())
        await db.mark_message_as_read(message.index, message.chat_id)
    messages = [{"chat": botname, "messages": messages} for botname, messages in chats.items()]
    return messages


async def get_bots_last_online(user_token: str):
    db: DB = DB.get_instance()
    bots_status = await db.get_bots_status(user_token)
    bots = []
    for bot in bots_status:
        bots.append({"botname": bot[1], "last_online": bot[0]})
    return bots


async def find_user_by_email_and_password(email: str, password_hash: str) -> User:
    db: DB = DB.get_instance()
    user_data = await db.find_user_by_email_and_password(email, password_hash)
    user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
    return user


async def create_chat(user_token: str, botname: str) -> str:
    db: DB = DB.get_instance()
    chat_id = token_urlsafe(15)
    new_chat = Chat(id=chat_id, botname=botname, user_token=user_token)
    await db.create_chat(new_chat)
    return chat_id


async def get_bot_by_bot_name(botname: str) -> Bot:
    db: DB = DB.get_instance()
    bot_data = await db.get_bot_by_bot_name(botname)
    bot = Bot(
        token=bot_data[0],
        botname=bot_data[1],
        title=bot_data[2],
        description=bot_data[3],
        owner_token=bot_data[4],
        last_online=bot_data[5],
    )
    return bot
