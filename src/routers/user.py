from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, status
# from pydantic import EmailStr

from db import DB
from models import User
from data_api import DataApi

user_router = APIRouter(prefix="/user", tags=['user'])


async def get_user(token: str) -> User:
    db: DB = DB.get_instance()
    user = await db.get_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
    return user


@user_router.post("/register")
async def register(email: str, password: str, name: str): # TODO change to mail
    db: DB = DB.get_instance()
    password_hash = sha256(password.encode()).hexdigest()
    user_token = await db.create_user(name=name, email=email, password_hash=password_hash)
    return {"token": user_token}


@user_router.post("/login")
async def login(email: str, password: str):  # TODO change to mail
    db: DB = DB.get_instance()
    password_hash = sha256(password.encode()).hexdigest()
    user = await db.find_user_by_email_and_password(email, password_hash)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {"token": user.token}


@user_router.put("/create_bot")
async def create_bot(botname: str, title: str, description: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    new_bot_token = await db.create_bot(user.token, botname, title, description)
    return {"bot_token": new_bot_token}


@user_router.delete("/delete_bot")
async def delete_bot(botname: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    bot = await db.get_bot_by_bot_name(botname)
    if bot is None or bot.owner_token != user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permissions to delete this bot"
        )
    deleted = await db.delete_bot(botname)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    return {"deleted": deleted}


@user_router.get("/bot_list")
async def bot_list(user=Depends(get_user)):
    db: DB = DB.get_instance()
    bots_list = []
    bots_objects = await db.get_bot_list(user_token=user.token)
    for bot in bots_objects:
        bots_list.append(bot.dict(exclude={"owner_token", "chats"}))
    return {"bots": bots_list}


@user_router.post("/push")
async def push_message_to_bot(message: str, botname: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    data_api: DataApi = DataApi.get_instance()

    bot = await db.get_bot_by_bot_name(botname)

    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="botname not found")
    try:
        await data_api.user_push(user, botname, message)
        # user.push_to_bot(botname=botname, message=message)
    except KeyError:
        await db.create_chat(user.token, botname)
        await data_api.user_push(user, botname, message)
        # user.push_to_bot(botname=botname, message=message)


@user_router.get("/bots_status")
async def bots_status(user=Depends(get_user)):
    db: DB = DB.get_instance()
    bots = await db.get_bots_last_online(user.token)
    return bots


@user_router.get("/bot_info")
async def bot_info(botname: str):
    db: DB = DB.get_instance()
    bot = await db.get_bot_by_bot_name(botname)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found.")
    return bot.dict(include={"title", "botname", "description", "last_online"})


@user_router.get("/pull")
async def pull_messages(user=Depends(get_user)):
    db: DB = DB.get_instance()
    messages = await db.get_user_unread_messages(user.token)
    return {"messages": messages}
