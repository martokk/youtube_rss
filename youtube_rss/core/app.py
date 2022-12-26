from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from loguru import logger

from youtube_rss.api.v1.api import api_router
from youtube_rss.config import BUILD_FEED_CACHE_INTERVAL_MINUTES
from youtube_rss.db.database import create_db_and_tables
from youtube_rss.paths import FEEDS_PATH
from youtube_rss.services.feed import build_all_rss_files

# Initialize FastAPI App
app = FastAPI()
app.include_router(api_router)
app.mount("/feed", StaticFiles(directory=FEEDS_PATH), name="feed")


@app.on_event("startup")  # type: ignore
async def on_startup() -> None:
    """
    On Statup:
        - create database and tables.
    """
    return await create_db_and_tables()


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=BUILD_FEED_CACHE_INTERVAL_MINUTES * 60, wait_first=True)
async def repeating_build_cache_for_all_feeds() -> None:
    """
    Repeat Every n seconds:
        - Build .rss file cache for all feeds/sources.
    """
    logger.info("Building (.rss) cache for all feeds.")
    build_all_rss_files()
    logger.success("Completed building (.rss) cache for all feeds.")


@app.get("/")
async def root() -> dict[str, str]:
    """
    Server root, return simple api status.
    """
    return {"api_status": "OK"}
