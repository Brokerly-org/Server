from secrets import token_urlsafe
from hashlib import sha256

import aiosqlite

from models import Bot, User, Chat


class DB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("DB is not initialized.")
        return cls._instance

    def __init__(self):
        self.db_file = "data.db"
        self.bots_by_botname = {}
        self.bots_by_token = {}
        self.users = {}
        self.chats = {}

        self.__class__._instance = self

    async def create_tables(self):
        async with aiosqlite.connect(self.db_file) as db:
            async with aiosqlite.connect(self.db_file) as db:
                sql = "CREATE TABLE users (token TEXT, name TEXT, email TEXT, password_hash TEXT)"
                await db.execute(sql)
                sql = "CREATE TABLE bots (token TEXT, botname TEXT, title TEXT, description TEXT, owner_token TEXT, last_online REAL)"
                await db.execute(sql)
                sql = "CREATE TABLE chats (id TEXT, botname TEXT, user_token TEXT, password_hash TEXT)"
                await db.execute(sql)

    async def _get_bot_by_bot_name(self, botname: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM bots WHERE botname=?"
            async with db.execute(sql, [botname]) as cursor:
                return await cursor.fetchone()

    async def _get_bot_by_token(self, token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM bots WHERE token=?"
            async with db.execute(sql, [token]) as cursor:
                return await cursor.fetchone()

    async def _get_user(self, token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM users WHERE token=?"
            async with db.execute(sql, [token]) as cursor:
                return await cursor.fetchone()

    async def _create_user(self, user: User):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "INSERT INTO users VALUES (?, ?, ?, ?)"
            await db.execute_insert(
                sql,
                [
                    user.token,
                    user.name,
                    user.email,
                    user.password_hash,
                ]
            )
            await db.commit()

    async def _create_bot(self, bot: Bot):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "INSERT INTO bots VALUES (?, ?, ?, ?, ?, ?)"
            await db.execute_insert(
                sql,
                [
                    bot.token,
                    bot.botname,
                    bot.title,
                    bot.description,
                    bot.owner_token,
                    bot.last_online,
                ]
            )
            await db.commit()

    async def _create_chat(self, chat: Chat):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "INSERT INTO chats VALUES (?, ?, ?, ?)"
            await db.execute_insert(
                sql,
                [
                    chat.id,
                    chat.botname,
                    chat.user_token,
                    chat.active,
                ]
            )
            await db.commit()

    async def _delete_bot(self, token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "DELETE FROM bots WHERE token=?"
            await db.execute(sql, [token])
            await db.commit()

    async def _delete_user(self, token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "DELETE FROM users WHERE token=?"
            await db.execute(sql, [token])
            await db.commit()

    async def _find_user_by_email_and_password(self, email: str, password_hash: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM users WHERE email=? AND password_hash=?"
            # TODO: limit 1
            async with db.execute(sql, [email, password_hash]) as cursor:
                user = await cursor.fetchone()
                return user

    async def create_admin_user(self):
        password = "admin"
        password_hash = sha256(password.encode()).hexdigest()
        new_user = User(token="admin", name="admin", email="admin@admin.com", password_hash=password_hash)
        self.users["admin"] = new_user
        await self._create_user(new_user)

    async def create_bot(self, user_token: str, botname: str, title: str, description: str) -> str:
        token = token_urlsafe(15)
        new_bot = Bot(token=token, botname=botname, title=title, description=description, owner_token=user_token)
        self.bots_by_botname[botname] = new_bot
        self.bots_by_token[token] = new_bot
        await self._create_bot(new_bot)
        self.users[user_token].add_bot(new_bot.token)
        return token

    async def find_user_by_email_and_password(self, email: str, password_hash: str) -> User:
        for user in self.users.values():
            if user.email == email and user.password_hash == password_hash:
                return user
        user_data = await self._find_user_by_email_and_password(email, password_hash)
        user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        # TODO: load user bot tokens
        return user

    async def create_user(self, name: str, email: str, password_hash: str) -> str:
        token = token_urlsafe(15)
        new_user = User(token=token, name=name, email=email, password_hash=password_hash)
        self.users[token] = new_user
        await self._create_user(new_user)
        return token

    async def new_chat(self, user_token: str, botname: str):
        chat_id = token_urlsafe(15)
        new_chat = Chat(id=chat_id, botname=botname, user_token=user_token)
        self.bots_by_botname[botname].add_chat(new_chat)
        self.users[user_token].add_chat(new_chat)
        await self._create_chat(new_chat)

    async def get_bot_by_bot_name(self, botname: str) -> Bot:
        bot = self.bots_by_botname.get(botname, None)
        if bot:
            return bot
        bot_data = await self._get_bot_by_bot_name(botname)
        # TODO: create Bot from Row
        return bot_data

    async def get_bot_by_token(self, bot_token: str) -> Bot:
        bot = self.bots_by_token.get(bot_token, None)
        if bot:
            return bot
        bot_data = await self._get_bot_by_token(bot_token)
        bot = Bot(
            token=bot_data[0],
            botname=bot_data[1],
            title=bot_data[2],
            description=bot_data[3],
            owner_token=bot_data[4],
            last_online=bot_data[5],
        )
        return bot

    async def get_user(self, user_token: str) -> User:
        user = self.users.get(user_token, None)
        if user:
            return user
        user_data = await self._get_user(user_token)
        user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        # TODO: load user bot tokens
        self.users[user.token] = user
        return user

    async def delete_bot(self, botname: str):
        bot = await self.get_bot_by_bot_name(botname)
        bot.delete()
        del self.bots_by_botname[botname]
        del self.bots_by_token[bot.token]
        await self._delete_bot(bot.token)
        return True

    def close(self):
        pass
