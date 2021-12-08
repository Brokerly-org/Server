from hashlib import sha256

from sqlmodel import Session, select

from core.models.database import get_db_engine
from core.schemas.bot import Bot
from core.schemas.user import User


def create_user(name: str, email: str, password: str) -> str:
    password_hash = sha256(password.encode()).hexdigest()
    with Session(get_db_engine()) as session:
        new_user = User(name=name, email=email, password_hash=password_hash)
        session.add(new_user)
        session.commit()
        return new_user.token


def get_user_by_email_and_password(email: str, password: str):
    password_hash = sha256(password.encode()).hexdigest()
    with Session(get_db_engine()) as session:
        get_user_query = select(User).where(User.email == email and User.password_hash == password_hash)
        user = session.exec(get_user_query).one_or_none()
        if user is None:
            raise ValueError("Invalid email or password")
        return user


def create_bot(user: User, botname: str, title: str, description: str) -> str:
    with Session(get_db_engine()) as session:
        new_bot = Bot(botname=botname, title=title, description=description, owner_token=user.token)
        session.add(new_bot)
        session.commit()
        return new_bot.token


def delete_bot(user: User, botname: str) -> bool:
    with Session(get_db_engine()) as session:
        get_bot_query = select(Bot).where(Bot.botname == botname and Bot.owner_token == user.token)
        bot = session.exec(get_bot_query).one_or_none()
        if not bot:
            raise ValueError("You do not have permissions to delete this bot")
        session.delete(bot)
        session.commit()
        return True


def get_my_bots(user: User):
    with Session(get_db_engine()) as session:
        get_my_bots_query = select(Bot).where(Bot.owner_token == user.token)
        bots = session.exec(get_my_bots_query).all()
        return bots
