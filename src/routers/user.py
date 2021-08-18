from fastapi import APIRouter, Depends, HTTPException, status
# from pydantic import EmailStr

from db import DB
from models import User
from data_api import DataApi

user_router = APIRouter(prefix="/user", tags=['user'])


def get_user(token: str) -> User:
    db: DB = DB.get_instance()
    user = db.get_user(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token")
    return user


@user_router.post("/register")
def register(email: str, password: str, name: str): # TODO change to mail
    db: DB = DB.get_instance()
    user_token = db.create_user(name=name, email=email, password=password)
    return {"token": user_token}


@user_router.post("/login")
def login(email: str, password: str): # TODO change to mail
    db: DB = DB.get_instance()
    user = db.find_user_by_email_and_password(email, password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {"token": user.token}


@user_router.put("/create_bot")
def create_bot(botname: str, title: str, description: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    new_bot_token = db.create_bot(user.token, botname, title, description)
    return {"bot_token": new_bot_token}


@user_router.delete("/delete_bot")
def delete_bot(botname: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    bot = db.get_bot_by_bot_name(botname)
    if bot is None or bot.owner_token != user.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permissions to delete this bot"
        )
    deleted = db.delete_bot(botname)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    return {"deleted": deleted}


@user_router.get("/bot_list")
def bot_list(user=Depends(get_user)):
    db: DB = DB.get_instance()
    bots = [db.get_bot_by_token(bot_token).dict(exclude={"owner_token", "chats"}) for bot_token in user.bot_tokens]
    return {"bots": bots}


@user_router.post("/push")
async def push_message_to_bot(message: str, botname: str, user=Depends(get_user)):
    db: DB = DB.get_instance()
    data_api: DataApi = DataApi.get_instance()

    if db.bots_by_botname.get(botname, None) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="botname not found")
    try:
        await data_api.user_push(user, botname, message)
        # user.push_to_bot(botname=botname, message=message)
    except KeyError:
        db.new_chat(user.token, botname)
        await data_api.user_push(user, botname, message)
        # user.push_to_bot(botname=botname, message=message)


@user_router.get("/bots_status")
def bots_status(user=Depends(get_user)):
    db: DB = DB.get_instance()
    bots_info = {}
    for chat in user.chats.values():
        bot = db.get_bot_by_bot_name(chat.botname)
        bots_info[bot.botname] = bot.last_online
    return bots_info


@user_router.get("/bot_info")
def bot_info(botname: str):
    db: DB = DB.get_instance()
    bot = db.get_bot_by_bot_name(botname)
    if bot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found.")
    return bot.dict(include={"title", "botname", "description", "last_online"})


@user_router.get("/pull")
def pull_messages(user=Depends(get_user)):
    return {"messages": user.pull_from_chats()}
