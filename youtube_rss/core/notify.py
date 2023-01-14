from typing import Any

from telegram import Bot
from telegram.error import BadRequest

from youtube_rss import settings
from youtube_rss.core.logger import logger


async def notify(text: str) -> Any:
    """Sends a message via Telegram using the given text as the message's content.
    Telegram API token and chat ID must be set before calling this function.

    Args:
        text (str): The message text to send.

    Returns:
        Any : the message object

    Raises:
        ValueError: If the chat with the Telegram bot has not been initialized by the user
    """
    if not settings.telegram_api_token or settings.telegram_chat_id == 0:
        logger.warning("TELEGRAM_API_TOKEN or TELEGRAM_CHAT_ID settings variables are not set.")
        return None

    bot = Bot(token=settings.telegram_api_token)

    try:
        return await bot.send_message(chat_id=settings.telegram_chat_id, text=text)
    except BadRequest as e:
        raise ValueError(
            "The chat with the Telegram bot has not been first initialized by the user. "
            "Please start a conversation with the bot before trying to send a message"
        ) from e
