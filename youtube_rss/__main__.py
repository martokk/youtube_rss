from youtube_rss.core.cli import typer_app
from youtube_rss.core.logger import logger

if __name__ == "__main__":
    logger.info("--- Start ---")
    logger.debug(f"Starting Typer App: '{typer_app.info.name}'...")
    typer_app()
