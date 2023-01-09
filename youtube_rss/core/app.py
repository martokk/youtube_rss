from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from loguru import logger

from youtube_rss.api.v1.api import api_router
from youtube_rss.config import REFRESH_SOURCES_INTERVAL_MINUTES, REFRESH_VIDEOS_INTERVAL_MINUTES
from youtube_rss.crud.source import refresh_all_sources, source_crud
from youtube_rss.crud.video import refresh_all_videos
from youtube_rss.db.database import create_db_and_tables
from youtube_rss.paths import FEEDS_PATH, LOG_FILE

# Configure Loguru Logger
logger.add(LOG_FILE, level="TRACE", rotation="50 MB")

# Initialize FastAPI App

app = FastAPI()
app.debug = True
app.include_router(api_router)
app.mount("/feed", StaticFiles(directory=FEEDS_PATH), name="feed")


@app.on_event("startup")  # type: ignore
async def on_startup() -> None:
    """
    On Startup:
        - create database and tables.
    """
    logger.info("--- Start FastAPI ---")
    logger.debug("Starting FastAPI App...")
    return await create_db_and_tables()


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=REFRESH_SOURCES_INTERVAL_MINUTES * 60, wait_first=True)
async def repeating_refresh_sources() -> None:
    """
    Fetches new data from yt-dlp for all Videos that meet criteria.
    """
    logger.debug("Refreshing Sources...")
    refreshed_videos = await refresh_all_sources()
    logger.success(f"Completed refreshing {len(refreshed_videos)} Sources from yt-dlp.")


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=REFRESH_VIDEOS_INTERVAL_MINUTES * 60, wait_first=True)
async def repeating_refresh_videos() -> None:
    """
    Fetches new data from yt-dlp for all Videos that meet criteria.
    """
    logger.debug("Refreshing Videos...")
    refreshed_videos = await refresh_all_videos(older_than_hours=8)
    logger.success(f"Completed refreshing {len(refreshed_videos)} Videos from yt-dlp.")


@app.get("/")
async def root() -> HTMLResponse:
    """
    Server root. Returns html response of all sources.

    Parameters:
        sources: List of sources to display

    Returns:
        HTMLResponse: HTML page with list of sources
    """
    sources = await source_crud.get_all() or []
    sources_html = "".join(
        f'<li><a href="{source.feed_url}">{source.name}</a>  |  <a href="{source.url}">{source.url}</a></li>'
        for source in sources
    )
    html = f"<html><header><title>RSS Feeds</title></header><body><h2>RSS Feeds</h2><ul>{sources_html}</ul></body></html>"
    return HTMLResponse(html)
