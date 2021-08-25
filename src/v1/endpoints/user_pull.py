from fastapi import APIRouter, Depends


from core.models.orm.user import UserModel
from ..validators import validate_user_token


user_pull_endpoint = APIRouter(tags=["user"])


@user_pull_endpoint.get("/pull")
async def pull_messages(user=Depends(validate_user_token)):
    messages = await UserModel.get_unread_messages(user.token)
    return {"messages": messages}
