from fastapi import APIRouter, Depends


from core.models.orm import get_user_unread_messages
from ..validators import validate_user_token


user_pull_endpoint = APIRouter(tags=["user"])


@user_pull_endpoint.get("/pull")
async def pull_messages(user=Depends(validate_user_token)):
    messages = await get_user_unread_messages(user.token)
    return {"messages": messages}
