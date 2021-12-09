from os import remove
import pytest
import asyncio

from core.settings import get_settings
from api.admins import (
    create_user,
    get_user_by_email_and_password,
    create_bot,
    delete_bot,
    get_my_bots,
)
from api.users import (
    get_user_by_token,
    get_unread_messages as user_get_unread_messages,
    send_message as user_send_message,
    get_number_of_unread_messages,
    get_bots_with_open_chat
)
from api.bots import (
    get_bot_by_token,
    get_bot_by_botname,
    get_unread_messages as bot_get_unread_messages,
    update_bot_online_status,
    send_message as bot_send_message,
)

USERNAME = "test_user"
EMAIL = "test_email"
PASSWORD = "test_password"
BOTNAME = "test_botname"
BOT_TITLE = "test title"
BOT_DESCRIPTION = "tes long description more text here"
MESSAGE = "test message"
DB_FILE = "data/test_data.db"


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def settings():
    get_settings().sqlite_db_file = DB_FILE
    yield get_settings()
    remove(DB_FILE)


@pytest.mark.asyncio
async def test_full_use(settings):
    # Create user
    user_token = create_user(USERNAME, EMAIL, PASSWORD)
    user = get_user_by_token(user_token)
    assert user.name == USERNAME
    assert user.email == EMAIL

    # Login to user
    user_token2 = get_user_by_email_and_password(EMAIL, PASSWORD).token
    assert user_token == user_token2
    with pytest.raises(ValueError):
        get_user_by_email_and_password(EMAIL, "wrong password")
    with pytest.raises(ValueError):
        get_user_by_email_and_password("wrong email", PASSWORD)

    # Create bot
    bot_token = create_bot(user, BOTNAME, BOT_TITLE, BOT_DESCRIPTION)
    bot1 = get_bot_by_token(bot_token)
    bot2 = get_bot_by_botname(BOTNAME)
    assert bot1.token == bot2.token
    assert bot1.botname == bot2.botname == BOTNAME
    assert bot1.title == bot2.title == BOT_TITLE
    assert bot1.description == bot2.description == BOT_DESCRIPTION

    # Check my bots list
    bots = get_my_bots(user)
    assert bots[0].token == bot1.token

    # Check bots with open chats list
    bots = get_bots_with_open_chat(user)
    assert len(bots) == 0

    # Send message to bot
    message_sent = await user_send_message(user, MESSAGE, BOTNAME)
    assert message_sent == True

    # Bot pull messages
    unread_messages = bot_get_unread_messages(bot1)
    assert len(unread_messages) == 1  # One chat
    chat_ids = list(unread_messages.keys())
    assert len(unread_messages[chat_ids[0]]) == 1  # One message
    message = unread_messages[chat_ids[0]][0]
    assert message["content"] == MESSAGE
    assert not message["read_status"]
    assert message["index"] == 0

    # No more unread messages
    um = bot_get_unread_messages(bot1)
    assert len(um) == 0

    # Bot send reply to user
    sent = await bot_send_message(bot1, MESSAGE, chat_ids[0])
    assert sent == True

    # Number of unread messages
    number_of_unread_messages = get_number_of_unread_messages(user)
    assert number_of_unread_messages == 1

    # User pull unread messages
    unread_messages = user_get_unread_messages(user)
    bots_botnames = list(unread_messages.keys())
    assert len(bots_botnames) == 1
    message = unread_messages[bots_botnames[0]][0]
    assert message["content"] == MESSAGE
    assert not message["read_status"]
    assert message["index"] == 1

    # Pull again
    unread_messages = user_get_unread_messages(user)
    assert len(unread_messages) == 0

    # Delete bot
    deleted = delete_bot(user, BOTNAME)
    assert deleted == True

    # Request deleted bot
    with pytest.raises(ValueError):
        get_bot_by_botname(BOTNAME)
