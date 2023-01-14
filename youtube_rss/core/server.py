import uvicorn

from youtube_rss import settings
from youtube_rss.core.logger import logger

# from rich.logging import RichHandler


def start_server() -> None:
    logger.debug("Starting uvicorn server...")

    uvicorn.run(
        settings.uvicorn_entrypoint,
        host=settings.server_host,
        port=settings.server_port,
        log_level=settings.log_level.lower(),
        reload=settings.uvicorn_reload,
        app_dir="",
    )
