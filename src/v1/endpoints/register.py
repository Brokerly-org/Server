from hashlib import sha256

from fastapi import APIRouter

# from pydantic import EmailStr

from core.models.orm.user import UserModel

register_endpoint = APIRouter(tags=["auth"])


@register_endpoint.post("/register")
async def register(email: str, password: str, name: str):  # TODO change to mail
    password_hash = sha256(password.encode()).hexdigest()
    user_token = await UserModel.create(name=name, email=email, password_hash=password_hash)
    return {"token": user_token}

