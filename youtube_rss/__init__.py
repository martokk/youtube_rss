"""A python project created by Martokk."""

from importlib import metadata as importlib_metadata
from os import getenv

from dotenv import load_dotenv

from youtube_rss.models.settings import Settings
from youtube_rss.paths import ENV_FILE


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()

# Load ENV_FILE from ENV, else from app.paths
env_file = getenv("ENV_FILE", ENV_FILE)
load_dotenv(dotenv_path=env_file)
settings = Settings()  # type: ignore
