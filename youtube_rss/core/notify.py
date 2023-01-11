from loguru import logger
from telegram import Bot, Message
from telegram.error import BadRequest

from youtube_rss.config import TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID


async def notify(text: str) -> Message | None:
    """Sends a message via Telegram using the given text as the message's content.
    Telegram API token and chat ID must be set before calling this function.

    Args:
        text (str): The message text to send.

    Returns:
        Message : the message object
    """
    if not TELEGRAM_API_TOKEN or TELEGRAM_CHAT_ID == 0:
        logger.warning("TELEGRAM_API_TOKEN or TELEGRAM_CHAT_ID config variables are not set.")
        return None

    bot = Bot(token=TELEGRAM_API_TOKEN)

    try:
        return await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except BadRequest as e:
        raise ValueError(
            "The chat with the Telegram bot has not been first initialized by the user. "
            "Please start a conversation with the bot before trying to send a message"
        ) from e
