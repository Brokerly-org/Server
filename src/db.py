from secrets import token_urlsafe
from models import Bot, User, Chat


class DB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("DB is not initialized.")
        return cls._instance

    def __init__(self):
        self.bots_by_botname = {}
        self.bots_by_token = {}
        self.users = {}
        self.chats = {}

        # for testing..
        self.create_admin_user()

        self.__class__._instance = self

    def create_admin_user(self):
        new_user = User(token="admin", name="admin", email="admin@admin.com", password="admin")
        self.users["admin"] = new_user

    def create_bot(self, user_token: str, botname: str, title: str, description: str) -> str:
        token = token_urlsafe(15)
        new_bot = Bot(token=token, botname=botname, title=title, description=description, owner_token=user_token)
        self.bots_by_botname[botname] = new_bot
        self.bots_by_token[token] = new_bot
        self.users[user_token].add_bot(new_bot.token)
        return token

    def find_user_by_email_and_password(self, email: str, password: str) -> User:
        for user in self.users.values():
            if user.email == email and user.password == password:
                return user

    def create_user(self, name: str, email: str, password: str) -> str:
        token = token_urlsafe(15)
        new_user = User(token=token, name=name, email=email, password=password)
        self.users[token] = new_user
        return token

    def new_chat(self, user_token: str, botname: str):
        chat_id = token_urlsafe(15)
        new_chat = Chat(id=chat_id, botname=botname, user_token=user_token)
        self.bots_by_botname[botname].add_chat(new_chat)
        self.users[user_token].add_chat(new_chat)

    def get_bot_by_bot_name(self, botname: str) -> Bot:
        return self.bots_by_botname.get(botname, None)

    def get_user(self, user_token: str) -> User:
        return self.users.get(user_token, None)

    def get_bot_by_token(self, bot_token: str) -> Bot:
        return self.bots_by_token.get(bot_token, None)

    def close(self):
        pass
