from typing import Any

import pickle
from pathlib import Path

from loguru import logger

from youtube_rss.config import BUILD_FEED_DATEAFTER, BUILD_FEED_RECENT_VIDEOS
from youtube_rss.db.crud import source_crud
from youtube_rss.models.source import Source
from youtube_rss.paths import SOURCE_INFO_CACHE_PATH
from youtube_rss.services.ytdlp import get_info_dict


async def get_source(source_id: str) -> Source:
    """
    Get Source obj from source_id
    """
    source = source_crud.get(source_id=source_id)
    if source is None:
        raise FileNotFoundError(f"Source ({source_id=}) was not found.")
    return source


async def get_source_metadata(url: str) -> dict[str, str]:
    return await get_info_dict(
        url=url,
        ydl_opts={
            "logger": logger,
            "outtmpl": "%(title)s%(ext)s",
            "format": "b",
            "skip_download": True,
            "playlistend": 0,
            "extract_flat": True,
            "playlistreverse": True,
        },
    )


async def get_source_info_dict(
    source_id: str,
    url: str,
    use_cache=False,
) -> dict[str, Any]:
    """
    Uses yt-dlp to get the info_dict from youtube url.
    """
    cache_file = Path(SOURCE_INFO_CACHE_PATH / source_id)

    if use_cache:
        try:
            return pickle.load(cache_file.open("rb"))
        except FileNotFoundError:
            pass

    try:
        info_dict = await get_info_dict(
            url=url,
            ydl_opts={
                "logger": logger,
                "outtmpl": "%(title)s%(ext)s",
                "format": "b",
                "skip_download": True,
                "playlistend": BUILD_FEED_RECENT_VIDEOS,
                "playlistreverse": True,
                "dateafter": BUILD_FEED_DATEAFTER,
            },
        )
    except ValueError as exc:
        raise ValueError(
            f"Youtube-DL did not download 'source_info' for feed ({source_id=})."
        ) from exc

    pickle.dump(info_dict, cache_file.open("wb"))
    return info_dict
