from fastapi import APIRouter, Depends, HTTPException, status

from core.schemas.user import User
from api.users import get_user_by_token
from api.admins import (
    get_my_bots,
    create_bot,
    delete_bot,
    create_user,
    get_user_by_email_and_password,
)


admin_router = APIRouter(tags=["admin"])


@admin_router.post("/auth/register")
def register(email: str, password: str, name: str):
    try:
        user_token = create_user(name, email, password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is all ready in use.")
    return {"token": user_token}


@admin_router.post("/auth/login")
def login(email: str, password: str):
    try:
        user = get_user_by_email_and_password(email, password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return {"token": user.token}


@admin_router.put("/admin/create_bot")
def new_bot(
    botname: str, title: str, description: str, user=Depends(get_user_by_token)
):
    bot_token = create_bot(user, botname, title, description)
    return {"bot_token": bot_token}


@admin_router.delete("/admin/delete_bot")
def delete(botname: str, user: User = Depends(get_user_by_token)):
    try:
        deleted = delete_bot(user, botname)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not have permissions to delete this bot",
        )
    return {"deleted": deleted}


@admin_router.get("/admin/bot_list")
async def bot_list(user=Depends(get_user_by_token)):
    bots = get_my_bots(user)
    return {"bots": [bot.dict(exclude={"owner_token": True}) for bot in bots]}
