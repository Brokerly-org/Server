from collections import defaultdict

from sqlmodel import Session, select

from core.models.database import get_db_engine
from core.schemas.bot import Bot
from core.schemas.message import Message
from core.schemas.chat import Chat


def get_bot_by_token(token: str) -> Bot:
    with Session(get_db_engine()) as session:
        get_bot_query = select(Bot).where(Bot.token == token)
        bot = session.exec(get_bot_query).one_or_none()
        if bot is None:
            raise ValueError("Invalid bot token")
        return bot


def get_bot_by_botname(botname: str) -> Bot:
    with Session(get_db_engine()) as session:
        get_bot_query = select(Bot).where(Bot.botname == botname)
        bot = session.exec(get_bot_query).one_or_none()
        if bot is None:
            raise ValueError("Invalid bot botname")
        return bot


def get_unread_messages(bot: Bot):
    with Session(get_db_engine()) as session:
        get_unread_messages_query = select(Message, Chat) \
            .where(Message.chat_id == Chat.id) \
            .where(Chat.botname == bot.botname) \
            .where(Message.read_status == False)

        results = session.exec(get_unread_messages_query).all()
        chats = defaultdict(list)
        for message, chat in results:
            chats[chat.id].append(message.dict())
            message.read_status = True
            session.add(message)

        session.commit()
        return chats


def send_message(bot: Bot, message: str, chat_id: str) -> bool:
    with Session(get_db_engine()) as session:
        get_chat_query = select(Chat).where(Chat.id == chat_id)
        chat = session.exec(get_chat_query).one_or_none()
        if chat is None or chat.botname != bot.botname:
            raise ValueError("Chat Id not found")

        new_message = Message(chat_id=chat.id, index=chat.size, sender="bot", read_status=False, content=message)
        session.add(new_message)

        chat.size += 1
        session.add(chat)  # Update chat size

        session.commit()
    return True
