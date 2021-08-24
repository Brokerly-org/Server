from hashlib import sha256

from fastapi import APIRouter, HTTPException, status

# from pydantic import EmailStr

from core.models.orm import try_login

login_endpoint = APIRouter(tags=["auth"])


@login_endpoint.post("/login")
async def login(email: str, password: str):  # TODO change to mail
    password_hash = sha256(password.encode()).hexdigest()
    user = await try_login(email, password_hash)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return {"token": user.token}
