from hashlib import sha256

from fastapi import APIRouter, HTTPException, status

# from pydantic import EmailStr

from models import User
from data_layer.user import (
    get_user as get_user_by_token,
    create_user,
    find_user_by_email_and_password,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def get_user(token: str) -> User:
    user = await get_user_by_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user token"
        )
    return user


@auth_router.post("/register")
async def register(email: str, password: str, name: str):  # TODO change to mail
    password_hash = sha256(password.encode()).hexdigest()
    user_token = await create_user(name=name, email=email, password_hash=password_hash)
    return {"token": user_token}


@auth_router.post("/login")
async def login(email: str, password: str):  # TODO change to mail
    password_hash = sha256(password.encode()).hexdigest()
    user = await find_user_by_email_and_password(email, password_hash)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return {"token": user.token}
