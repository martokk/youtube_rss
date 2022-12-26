from typing import Any

import pickle
from pathlib import Path

from loguru import logger
from yt_dlp import YoutubeDL

from youtube_rss.config import BUILD_FEED_DATEAFTER, BUILD_FEED_RECENT_VIDEOS
from youtube_rss.db.crud import source_crud
from youtube_rss.models.source import Source
from youtube_rss.paths import SOURCE_INFO_CACHE_PATH

YDL_OPTS_SOURCE = {
    "logger": logger,
    "outtmpl": "%(title)s%(ext)s",
    "format": "b",
    "skip_download": True,
    "playlistend": BUILD_FEED_RECENT_VIDEOS,
    "playlistreverse": True,
    "dateafter": BUILD_FEED_DATEAFTER,
}

YDL_OPTS_SOURCE_METADATA = {
    "logger": logger,
    "outtmpl": "%(title)s%(ext)s",
    "format": "b",
    "skip_download": True,
    "playlistend": 0,
    "extract_flat": True,
    "playlistreverse": True,
}


def get_source(source_id: str) -> Source:
    """
    Get Source obj from source_id
    """
    source = source_crud.get(source_id=source_id)
    if source is None:
        raise FileNotFoundError(f"Source ({source_id=}) was not found.")
    return source


def get_info_dict(url: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

    if info_dict is None:
        raise ValueError(
            f"yt-dlp did not download a info_dict object. {info_dict=} {url=} {ydl_opts=}"
        )
    return info_dict


def get_source_metadata(url: str) -> dict[str, str]:
    return get_info_dict(url=url, ydl_opts=YDL_OPTS_SOURCE_METADATA)


def get_source_info_dict(
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
        info_dict = get_info_dict(url=url, ydl_opts=YDL_OPTS_SOURCE)
    except ValueError as exc:
        raise ValueError(
            f"Youtube-DL did not download 'source_info' for feed ({source_id=})."
        ) from exc

    pickle.dump(info_dict, cache_file.open("wb"))
    return info_dict
