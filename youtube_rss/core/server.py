import uvicorn
from loguru import logger
from rich.logging import RichHandler

from youtube_rss.config import SERVER_IP, SERVER_PORT

handler = RichHandler(level="DEBUG")
logger.add(handler)
logger.bind()


def start_server() -> None:
    logger.debug("Starting uvicorn server...")
    uvicorn.run(
        "youtube_rss.core.app:app",
        host=SERVER_IP,
        port=SERVER_PORT,
        log_level="debug",
        reload=True,
        app_dir="",
    )
