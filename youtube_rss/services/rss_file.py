from pathlib import Path

from loguru import logger

from youtube_rss.crud.source import source_crud
from youtube_rss.paths import FEEDS_PATH
from youtube_rss.services.feed import SourceFeedGenerator


async def get_rss_file_path(source_id: str) -> Path:
    """
    Returns the file path for a 'source_id' rss file.
    """
    return FEEDS_PATH / f"{source_id}.rss"


async def get_rss_file(source_id: str) -> Path:
    """
    Returns a validated rss file.
    """
    rss_file = await get_rss_file_path(source_id=source_id)

    # Validate RSS File exists
    if not rss_file.exists():
        err_msg = f"RSS file ({source_id}.rss) does not exist for ({source_id=})"
        logger.warning(err_msg)
        raise FileNotFoundError(err_msg)
    return rss_file


async def delete_rss_file(source_id: str):
    rss_file = await get_rss_file_path(source_id=source_id)
    rss_file.unlink()


async def build_rss_file(source_id: str) -> Path:
    """
    Builds a .rss file for source_id, saves it to disk.
    """
    source = await source_crud.get(id=source_id)
    feed = SourceFeedGenerator(source=source)
    rss_file = await feed.save()
    return rss_file
