import uvicorn
from loguru import logger
from rich.logging import RichHandler

from youtube_rss.config import LOG_LEVEL, SERVER_IP, SERVER_PORT, UVICORN_ENTRYPOINT, UVICORN_RELOAD

handler = RichHandler(level=LOG_LEVEL)
logger.add(handler)
logger.bind()


def start_server() -> None:
    logger.debug("Starting uvicorn server...")
    uvicorn.run(
        UVICORN_ENTRYPOINT,
        host=SERVER_IP,
        port=SERVER_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=UVICORN_RELOAD,
        app_dir="",
    )
