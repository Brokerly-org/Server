from fastapi import APIRouter, Depends

from core.schemas.bot import Bot
from core.schemas.message import InputMessage

from api.bots import get_bot_by_token, get_unread_messages, send_message


bot_router = APIRouter(tags=["bot"])


# @bot_router.post("/callback")
# async def push_callback_as_bot(chat_id: str, data: dict, bot: Bot = Depends(validate_bot_token)):
#     with Session(get_db_engine()) as session:
#         get_chat_query = select(Chat).where(Chat.id == chat_id)
#         chat = session.exec(get_chat_query).one_or_none()
#         if chat is None or chat.botname != bot.botname:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail="Chat Id not found"
#             )
#         # TODO: push callback data to chat
#     return {"sent": True}


@bot_router.get("/pull")
def pull_messages_as_bot(bot: Bot = Depends(get_bot_by_token)):
    unread_messages = get_unread_messages(bot)
    return {"chats": unread_messages}


@bot_router.post("/push")
async def push_message_as_bot(chat_id: str, message: InputMessage, bot: Bot = Depends(get_bot_by_token)):
    sent: bool = send_message(bot, message.text, chat_id)
    return {"sent": sent}
