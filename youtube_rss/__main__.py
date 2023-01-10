from loguru import logger

from youtube_rss.config import LOG_LEVEL
from youtube_rss.core.cli import typer_app
from youtube_rss.paths import LOG_FILE

# Configure Loguru Logger
logger.add(LOG_FILE, level=LOG_LEVEL, rotation="50 MB")
logger.info(f"Log level set by .env to '{LOG_LEVEL}'")

if __name__ == "__main__":
    logger.info("--- Start ---")
    logger.debug(f"Starting Typer App: '{typer_app.info.name}'...")
    typer_app()
