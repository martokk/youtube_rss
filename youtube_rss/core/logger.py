from loguru import logger as _logger

from youtube_rss import settings
from youtube_rss.paths import LOG_FILE

_logger.add(LOG_FILE, level=settings.log_level, rotation="10 MB")
_logger.info(f"Log level set by .env to '{settings.log_level}'")

logger = _logger
