from collections import defaultdict

from sqlmodel import Session, select

from events import dispatch
from core.models.database import get_db_engine
from core.schemas.user import User
from core.schemas.chat import Chat
from core.schemas.bot import Bot
from core.schemas.message import Message


def get_user_by_token(token: str):
    with Session(get_db_engine()) as session:
        get_user_query = select(User).where(User.token == token)
        user = session.exec(get_user_query).one_or_none()
        if user is None:
            raise ValueError("Invalid user token")
        return user


async def send_message(user: User, message: str, botname: str) -> bool:
    with Session(get_db_engine()) as session:
        get_chat_query = select(Chat).where(Chat.botname == botname and Chat.user_token == user.token)
        chat = session.exec(get_chat_query).first()
        if chat is None:
            get_bot_query = select(Bot).where(Bot.botname == botname)
            bot = session.exec(get_bot_query).first()
            if bot is None:
                raise ValueError("botname not found")
            chat = Chat(user_token=user.token, botname=botname)
            session.add(chat)

        new_message = Message(chat_id=chat.id, index=chat.size, sender="user", read_status=False, content=message)
        session.add(new_message)

        chat.size += 1
        session.add(chat)

        session.commit()
    await dispatch(botname)
    return True


def get_unread_messages(user: User):
    with Session(get_db_engine()) as session:
        get_unread_messages_query = select(Message, Chat) \
            .where(Message.chat_id == Chat.id) \
            .where(Chat.user_token == user.token) \
            .where(Message.read_status == False)
        results = session.exec(get_unread_messages_query).all()

        bots = defaultdict(list)
        for message, chat in results:
            bots[chat.botname].append(message.dict())
            message.read_status = True
            session.add(message)

        session.commit()
        return bots


def get_bots_with_open_chat(user: User):
    with Session(get_db_engine()) as session:
        get_bots_query = select(Bot, Chat)\
            .where(Bot.botname == Chat.botname)\
            .where(Chat.user_token == user.token)
        result = session.exec(get_bots_query).all()
        bots = []
        for bot, chat in result:
            bots.append(bot)
        return bots


def get_number_of_unread_messages(user: User) -> int:
    with Session(get_db_engine()) as session:
        get_unread_messages_query = select(Message, Chat)\
            .where(Message.chat_id == Chat.id)\
            .where(Chat.user_token == user.token)\
            .where(Message.read_status == False)
        return len(session.exec(get_unread_messages_query).all())


def get_bot_by_botname(botname: str) -> Bot:
    with Session(get_db_engine()) as session:
        get_bot_info_query = select(Bot).where(Bot.botname == botname)
        bot = session.exec(get_bot_info_query).first()
        if bot is None:
            raise ValueError("Bot not found.")
        return bot
