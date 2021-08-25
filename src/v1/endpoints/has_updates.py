from fastapi import APIRouter, Depends

from core.models.orm.user import UserModel

from ..validators import validate_user_token


has_updates_endpoint = APIRouter(tags=["user"])


@has_updates_endpoint.get("/has_updates")
async def has_updates(user=Depends(validate_user_token)):
    return await UserModel.get_updates_count(user.token)
