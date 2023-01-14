from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_utils.tasks import repeat_every
from sqlmodel import Session

from youtube_rss import settings, version
from youtube_rss.api.deps import get_db
from youtube_rss.api.v1.router import api_router
from youtube_rss.core.database import create_db_and_tables
from youtube_rss.core.logger import logger
from youtube_rss.core.notify import notify
from youtube_rss.models.server import HealthCheck
from youtube_rss.paths import DATABASE_FILE, FEEDS_PATH
from youtube_rss.services.source import refresh_all_sources
from youtube_rss.services.videos import refresh_all_videos
from youtube_rss.views.router import views_router

# Initialize FastAPI App
app = FastAPI(
    title=settings.project_name,
    version=version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    debug=settings.debug,
)
app.include_router(api_router)
app.include_router(views_router)
app.mount("/feed", StaticFiles(directory=FEEDS_PATH), name="feed")


@app.on_event("startup")  # type: ignore
async def on_startup() -> None:
    """
    On Startup:
        - create database and tables.
    """
    logger.info("--- Start FastAPI ---")
    logger.debug("Starting FastAPI App...")
    if settings.notify_on_start:
        await notify(text=f"{settings.project_name}('{settings.env_name}') started.")

    if not DATABASE_FILE.exists():
        await create_db_and_tables()


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=settings.refresh_sources_interval_minutes * 60, wait_first=True)
async def repeating_refresh_sources(db: Session = Depends(get_db)) -> None:
    """
    Fetches new data from yt-dlp for all Videos that meet criteria.
    """
    logger.debug("Refreshing Sources...")
    refreshed_videos = await refresh_all_sources(db=db)
    logger.success(f"Completed refreshing {len(refreshed_videos)} Sources from yt-dlp.")


@app.on_event("startup")  # type: ignore
@repeat_every(seconds=settings.refresh_videos_interval_minutes * 60, wait_first=True)
async def repeating_refresh_videos(db: Session = Depends(get_db)) -> None:
    """
    Fetches new data from yt-dlp for all Videos that meet criteria.
    """
    logger.debug("Refreshing Videos...")
    refreshed_videos = await refresh_all_videos(older_than_hours=8, db=db)
    logger.success(f"Completed refreshing {len(refreshed_videos)} Videos from yt-dlp.")


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check() -> dict[str, str]:
    return {
        "name": settings.project_name,
        "version": version,
        "description": settings.project_description,
    }
