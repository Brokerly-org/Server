from secrets import token_urlsafe
from hashlib import sha256

from models import User, Bot
from db import DB


async def create_admin_user():
    db: DB = DB.get_instance()
    password = "admin"
    password_hash = sha256(password.encode()).hexdigest()
    new_user = User(
        token="admin",
        name="admin",
        email="admin@admin.com",
        password_hash=password_hash,
    )
    await db.create_user(new_user)


async def create_bot(
    user_token: str, botname: str, title: str, description: str
) -> str:
    db: DB = DB.get_instance()
    token = token_urlsafe(15)
    new_bot = Bot(
        token=token,
        botname=botname,
        title=title,
        description=description,
        owner_token=user_token,
    )
    await db.create_bot(new_bot)
    return token


async def delete_bot(botname: str):
    db: DB = DB.get_instance()
    await db.delete_bot(botname)
    return True


async def get_bot_list(user_token: str):
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
