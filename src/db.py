from secrets import token_urlsafe
from hashlib import sha256
from collections import defaultdict

import aiosqlite

from models import Bot, User, Chat, Message


class DB:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("DB is not initialized.")
        return cls._instance

    def __init__(self):
        self.db_file = "data/data.db"

        self.__class__._instance = self

    async def create_tables(self):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "CREATE TABLE users (token TEXT, name TEXT, email TEXT, password_hash TEXT)"
            await db.execute(sql)
            sql = "CREATE TABLE bots (token TEXT, botname TEXT, title TEXT, description TEXT, owner_token TEXT, last_online REAL)"
            await db.execute(sql)
            sql = "CREATE TABLE chats (id TEXT, botname TEXT, user_token TEXT, active BOOL, size INT)"
            await db.execute(sql)
            sql = "CREATE TABLE messages (chat_id TEXT, message_index INT, sender TEXT, content TEXT, read_status BOOL, created_at REAL)"
            await db.execute(sql)
            await db.commit()

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

    async def _get_chat(self, user_token: str, botname: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM chats WHERE user_token = ? AND botname = ?"
            async with db.execute(sql, [user_token, botname]) as cursor:
                return await cursor.fetchone()

    async def _get_bots_status(self, user_token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = """
            SELECT bots.last_online, bots.botname
            FROM bots
            INNER JOIN chats ON 
            bots.botname = chats.botname 
            INNER JOIN users ON
            users.token = chats.user_token AND users.token = ?
            """
            async with db.execute(sql, [user_token]) as cursor:
                return await cursor.fetchall()

    async def _get_chat_by_id(self, chat_id: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM chats WHERE id = ?"
            async with db.execute(sql, [chat_id]) as cursor:
                return await cursor.fetchone()

    async def _get_bot_unread_messages(self, botname: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = """
            SELECT messages.content, messages.message_index, messages.sender, messages.created_at, chats.id
            FROM messages
            INNER JOIN chats ON 
            messages.chat_id = chats.id AND messages.read_status = FALSE AND messages.sender = 'user'
            INNER JOIN bots ON 
            bots.botname = chats.botname AND bots.botname = ?
            """
            async with db.execute(sql, [botname]) as cursor:
                messages = await cursor.fetchall()
                return messages

    async def _get_user_unread_messages(self, user_token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = """
            SELECT messages.content, messages.message_index, messages.sender, messages.created_at, chats.id, chats.botname
            FROM messages
            INNER JOIN chats ON 
            messages.chat_id = chats.id AND messages.read_status = FALSE AND messages.sender = 'bot'
            INNER JOIN users ON 
            users.token = chats.user_token AND users.token = ?
            """
            async with db.execute(sql, [user_token]) as cursor:
                messages = await cursor.fetchall()
                return messages

    async def _mark_message_as_read(self, message_index: int, chat_id: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "UPDATE messages SET read_status = TRUE WHERE message_index = ? AND chat_id = ?"
            await db.execute(sql, [message_index, chat_id])
            await db.commit()

    async def _get_bot_list(self, user_token: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "SELECT * FROM bots WHERE owner_token=?"
            async with db.execute(sql, [user_token]) as cursor:
                return await cursor.fetchall()

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
            sql = "INSERT INTO chats VALUES (?, ?, ?, ?, ?)"
            await db.execute_insert(
                sql,
                [
                    chat.id,
                    chat.botname,
                    chat.user_token,
                    chat.active,
                    chat.size
                ]
            )
            await db.commit()

    async def _create_message(self, message: Message):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)"
            await db.execute_insert(
                sql,
                [
                    message.chat_id,
                    message.index,
                    message.sender,
                    message.content,
                    message.read_status,
                    message.created_at
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

    async def _update_bot_last_online(self, botname: str, unix_time: float):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "UPDATE bots SET last_online=? WHERE botname=?"
            await db.execute(sql, [unix_time, botname])
            await db.commit()

    async def _update_chat_size(self, chat_id: str):
        async with aiosqlite.connect(self.db_file) as db:
            sql = "UPDATE chats SET size = size + 1 WHERE id = ?"
            await db.execute(sql, [chat_id])
            await db.commit()

    async def find_user_by_email_and_password(self, email: str, password_hash: str) -> User:
        user_data = await self._find_user_by_email_and_password(email, password_hash)
        user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        # TODO: load user bot tokens
        return user

    async def create_admin_user(self):
        password = "admin"
        password_hash = sha256(password.encode()).hexdigest()
        new_user = User(token="admin", name="admin", email="admin@admin.com", password_hash=password_hash)
        await self._create_user(new_user)

    async def create_bot(self, user_token: str, botname: str, title: str, description: str) -> str:
        token = token_urlsafe(15)
        new_bot = Bot(token=token, botname=botname, title=title, description=description, owner_token=user_token)
        await self._create_bot(new_bot)
        return token

    async def create_user(self, name: str, email: str, password_hash: str) -> str:
        token = token_urlsafe(15)
        new_user = User(token=token, name=name, email=email, password_hash=password_hash)
        await self._create_user(new_user)
        return token

    async def create_message(self, chat_id: str, index: int, sender: str, content: str):
        new_message = Message(chat_id=chat_id, index=index, content=content, sender=sender, read_status=False)
        await self._create_message(new_message)
        await self._update_chat_size(chat_id)

    async def create_chat(self, user_token: str, botname: str) -> str:
        chat_id = token_urlsafe(15)
        new_chat = Chat(id=chat_id, botname=botname, user_token=user_token)
        await self._create_chat(new_chat)
        return chat_id

    async def get_bot_by_bot_name(self, botname: str) -> Bot:
        bot_data = await self._get_bot_by_bot_name(botname)
        bot = Bot(
            token=bot_data[0],
            botname=bot_data[1],
            title=bot_data[2],
            description=bot_data[3],
            owner_token=bot_data[4],
            last_online=bot_data[5],
        )
        return bot

    async def get_bot_by_token(self, bot_token: str) -> Bot:
        bot_data = await self._get_bot_by_token(bot_token)
        if not bot_data:
            return
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
        user_data = await self._get_user(user_token)
        if not user_data:
            return
        user = User(token=user_data[0], name=user_data[1], email=user_data[2], password_hash=user_data[3])
        # TODO: load user bot tokens
        return user

    async def get_bot_list(self, user_token: str):
        bot_list_data = await self._get_bot_list(user_token)
        bots = []
        for bot_data in bot_list_data:
            bot = Bot(
                token=bot_data[0],
                botname=bot_data[1],
                title=bot_data[2],
                description=bot_data[3],
                owner_token=bot_data[4],
                last_online=bot_data[5],
            )
            bots.append(bot)
        return bots

    async def get_bot_unread_messages(self, botname: str):
        messages_data = await self._get_bot_unread_messages(botname)
        chats = defaultdict(list)
        for message in messages_data:
            message = Message(
                content=message[0],
                index=message[1],
                sender=message[2],
                created_at=message[3],
                chat_id=message[4],
                read_status=False,
            )
            chats[message.chat_id].append(message.dict())
            await self._mark_message_as_read(message.index, message.chat_id)
        messages = [{"chat": chat_id, "messages": messages} for chat_id, messages in chats.items()]
        return messages

    async def get_bots_last_online(self, user_token: str):
        bots_status = await self._get_bots_status(user_token)
        bots = []
        for bot in bots_status:
            bots.append({"botname": bot[1], "last_online": bot[0]})
        return bots

    async def get_user_unread_messages(self, user_token: str):
        messages_data = await self._get_user_unread_messages(user_token)
        chats = defaultdict(list)
        for message in messages_data:
            botname = message[5]
            message = Message(
                content=message[0],
                index=message[1],
                sender=message[2],
                created_at=message[3],
                chat_id=message[4],
                read_status=False,
            )
            chats[botname].append(message.dict())
            await self._mark_message_as_read(message.index, message.chat_id)
        messages = [{"chat": botname, "messages": messages} for botname, messages in chats.items()]
        return messages

    async def get_chat_by_user_token_and_botname(self, user_token: str, botname:str) -> Chat:
        chat_data = await self._get_chat(user_token, botname)
        if not chat_data:
            return
        chat = Chat(
            id=chat_data[0],
            botname=chat_data[1],
            user_token=chat_data[2],
            active=chat_data[3],
            size=chat_data[4]
        )
        return chat

    async def get_chat_by_chat_id(self, chat_id: str) -> Chat:
        chat_data = await self._get_chat_by_id(chat_id)
        if not chat_data:
            return
        chat = Chat(
            id=chat_data[0],
            botname=chat_data[1],
            user_token=chat_data[2],
            active=chat_data[3],
            size=chat_data[4]
        )
        return chat

    async def update_bot_last_online(self, botname: str, unix_time: float):
        await self._update_bot_last_online(botname, unix_time)

    async def delete_bot(self, botname: str):
        bot = await self.get_bot_by_bot_name(botname)
        bot.delete()
        await self._delete_bot(bot.token)
        return True

    def close(self):
        pass
