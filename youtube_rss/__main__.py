from loguru import logger

from youtube_rss.core.cli import typer_app
from youtube_rss.paths import LOG_FILE

# Configure Loguru Logger
logger.add(LOG_FILE, level="TRACE", rotation="50 MB")


if __name__ == "__main__":
    logger.info("--- Start ---")
    logger.debug(f"Starting Typer App: '{typer_app.info.name}'...")
    typer_app()
