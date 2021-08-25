from time import time

from core.models.database import DB
from core.schemas.message import Message, InputMessage
from core.schemas.widget import Widget


__all__ = ["MessageModel"]


class MessageModel:
    @classmethod
    async def create(cls, chat_id: str, index: int, sender: str, content: InputMessage):
        db: DB = DB.get_instance()
        await db.create_message(chat_id, index, sender, content.text, False, time(),
                                content.widget.json() if content.widget else "non")
        await db.increase_chat_size(chat_id)

    @classmethod
    async def mark_as_read(cls, message_id: int, chat_id: str):
        db: DB = DB.get_instance()
        await db.mark_message_as_read(message_id, chat_id)

    @classmethod
    async def load_from_raw(cls, raw_message: list) -> Message:
        message = Message(
            content=raw_message[0],
            index=raw_message[1],
            sender=raw_message[2],
            created_at=raw_message[3],
            chat_id=raw_message[4],
            widget=Widget.parse_raw(raw_message[5]) if len(raw_message) > 5 and raw_message[5] != "non" else None,
            read_status=False,
        )
        return message
