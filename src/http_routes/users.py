from fastapi import APIRouter, Depends, HTTPException, status

from api.users import (
    send_message,
    get_bot_by_botname,
    get_bots_with_open_chat,
    get_number_of_unread_messages,
    get_unread_messages,
    get_user_by_token,
)


user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("/push")
async def push_message_to_bot(message: str, botname: str, user=Depends(get_user_by_token)):
    try:
        reslut: bool = send_message(user, message, botname)
    except ValueError as VE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="botname not found"
        )

    return {"sent": reslut}


@user_router.get("/pull")
async def pull_messages(user=Depends(get_user_by_token)):
    unread_messages = get_unread_messages(user)
    return {"bots": unread_messages}


@user_router.get("/bots_status")
def get_bots_status(user=Depends(get_user_by_token)):
    bots = get_bots_with_open_chat(user)
    return [{"botname": bot.botname, "online_status": bot.online_status} for bot in bots]


@user_router.get("/has_updates")
def has_updates(user=Depends(get_user_by_token)):
    number_of_updates = get_number_of_unread_messages(user)
    return number_of_updates > 0


@user_router.get("/bot_info")
def bot_info(botname: str):
    try:
        bot = get_bot_by_botname(botname)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="botname not found"
        )
    return {
        "title": bot.title,
        "botname": bot.botname,
        "description": bot.description,
        "online_status": bot.online_status,
    }
