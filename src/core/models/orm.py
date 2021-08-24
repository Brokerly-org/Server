from collections import defaultdict
from secrets import token_urlsafe
from time import time

from core.models.database import DB

from core.schemas.user import User
from core.schemas.bot import Bot
from core.schemas.message import Message, InputMessage
from core.schemas.chat import Chat
from core.schemas.widget import Widget


async def load_user_by_token(user_token: str) -> User:
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


async def load_bot_by_token(bot_token: str) -> Bot:
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


async def load_chat_by_botname_and_user_token(botname: str, user_token: str) -> Chat:
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


async def load_chat_by_id(chat_id: str):
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


async def load_bot_by_bot_name(botname: str) -> Bot:
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
        last_online=bot_data[5],
    )
    return bot


async def update_bot_last_online(botname: str, new_time):
    db: DB = DB.get_instance()
    await db.update_bot_last_online(botname, new_time)


async def mark_message_as_read(message_id: int, chat_id: str):
    db: DB = DB.get_instance()
    await db.mark_message_as_read(message_id, chat_id)


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
        await mark_message_as_read(message.index, message.chat_id)
        chats[message.chat_id].append(message.dict())
    messages = [
        {"chat": chat_id, "messages": messages} for chat_id, messages in chats.items()
    ]
    return messages


async def get_user_unread_messages(user_token: str):
    db: DB = DB.get_instance()
    messages_data = await db.get_user_unread_messages(user_token)
    chats = defaultdict(list)
    for message in messages_data:
        botname = message[6]
        message = Message(
            content=message[0],
            index=message[1],
            sender=message[2],
            created_at=message[3],
            widget=Widget.parse_raw(message[4]) if message[4] != "non" else None,
            chat_id=message[5],
            read_status=False,
        )
        chats[botname].append(message.dict(exclude={"chat_id", "read_status"}))
        await db.mark_message_as_read(message.index, message.chat_id)
    messages = [
        {"chat": botname, "messages": messages} for botname, messages in chats.items()
    ]
    return messages


async def delete_bot(botname: str):
    db: DB = DB.get_instance()
    await db.delete_bot(botname)
    return True


async def get_my_bot_list(user_token: str):
    db: DB = DB.get_instance()
    bot_list_data = await db.get_bot_list(user_token)
    bots = []
    for bot_data in bot_list_data:
        bot = Bot(
            token=bot_data[0],
            botname=bot_data[1],
            title=bot_data[2],
            description=bot_data[3],
            owner_token=bot_data[4],
            last_online=bot_data[5],
        )
        bots.append(bot)
    return bots


async def get_bots_last_online(user_token: str):
    db: DB = DB.get_instance()
    bots_status = await db.get_bots_status(user_token)
    bots = []
    for bot in bots_status:
        bots.append({"botname": bot[1], "last_online": bot[0]})
    return bots


async def get_user_updates_count(user_token: str) -> int:
    db: DB = DB.get_instance()
    return await db.get_user_unread_messages_count(user_token)


async def try_login(email: str, password_hash: str) -> User:
    db: DB = DB.get_instance()
    user_data = await db.find_user_by_email_and_password(email, password_hash)
    if user_data is None:
        return
    user = User(
        token=user_data[0],
        name=user_data[1],
        email=user_data[2],
        password_hash=user_data[3],
    )
    return user


async def create_user(name: str, email: str, password_hash: str) -> str:
    db: DB = DB.get_instance()
    token = token_urlsafe(15)
    await db.create_user(token, name, email, password_hash)
    return token


async def create_chat(user_token: str, botname: str) -> str:
    db: DB = DB.get_instance()
    chat_id = token_urlsafe(15)
    await db.create_chat(chat_id, botname, user_token, True, 0)
    return chat_id


async def create_bot(
    user_token: str, botname: str, title: str, description: str
) -> str:
    db: DB = DB.get_instance()
    token = token_urlsafe(15)
    await db.create_bot(token, botname, title, description, user_token, last_online=0)
    return token


async def create_message(chat_id: str, index: int, sender: str, content: InputMessage):
    db: DB = DB.get_instance()
    await db.create_message(chat_id, index, sender, content.text, False, time(), content.widget.json() if content.widget else "non")
    await db.increase_chat_size(chat_id)
