from typing import Any

import pickle
from datetime import datetime
from pathlib import Path

from youtube_rss.config import BUILD_FEED_DATEAFTER, BUILD_FEED_RECENT_VIDEOS
from youtube_rss.core.debug_helpers import log_function_enter_exit
from youtube_rss.models.source import Source, SourceOrderBy, generate_source_id_from_url
from youtube_rss.models.video import Video
from youtube_rss.paths import SOURCE_INFO_CACHE_PATH
from youtube_rss.services.ytdlp import YDL_OPTS_BASE, get_info_dict


async def get_source_ydl_opts(extract_flat: bool) -> dict[str, Any]:
    """
    Get the yt-dlp options for a source.

    Parameters:
        extract_flat (bool): Whether to extract a flat list of videos in the playlist.

    Returns:
        dict: The yt-dlp options for the source.
    """
    return {
        **YDL_OPTS_BASE,
        "playlistreverse": True,
        "extract_flat": extract_flat,
        "playlistend": BUILD_FEED_RECENT_VIDEOS,
        "dateafter": BUILD_FEED_DATEAFTER,
    }


@log_function_enter_exit()
async def get_source_info_dict(
    source_id: str | None,
    url: str,
    extract_flat: bool,
    use_cache=False,
) -> dict[str, Any]:
    """
    Retrieve the info_dict from yt-dlp for a Source

    Parameters:
        source_id (Union[str, None]): An optional ID for the source. If not provided,
            a unique ID will be generated from the URL.
        url (str): The URL of the Source
        extract_flat (bool): Whether to extract a flat list of videos in the playlist.
        use_cache (bool, optional): Whether to use a cached version of the info dictionary
            if it is available. Defaults to False.

    Returns:
        dict: The info dictionary for the Source

    """
    source_id = await generate_source_id_from_url(url=url)
    cache_file = Path(SOURCE_INFO_CACHE_PATH / source_id)

    # Load Cache
    if use_cache and cache_file.exists():
        return pickle.loads(cache_file.read_bytes())

    # Get info_dict from yt-dlp
    ydl_opts = await get_source_ydl_opts(extract_flat=extract_flat)
    info_dict = await get_info_dict(url=url, ydl_opts=ydl_opts)

    # Save Pickle
    cache_file.write_bytes(pickle.dumps(info_dict))
    return info_dict


async def get_source_from_source_info_dict(source_info_dict: dict[str, Any]) -> Source:
    """
    Get a `Source` object from a source_info_dict.

    Parameters:
        source_info_dict (dict): The source_info_dict.

    Returns:
        Source: The `Source` object.
    """
    source_videos = await get_source_videos_from_source_info_dict(source_info_dict=source_info_dict)
    return Source(
        url=source_info_dict["url"],
        name=source_info_dict["title"],
        author=source_info_dict["uploader"],
        logo=source_info_dict["thumbnails"][2]["url"],
        ordered_by=SourceOrderBy.RELEASE.value,
        description=source_info_dict["description"],
        videos=source_videos,
        extractor=source_info_dict["extractor_key"],
    )


async def get_source_videos_from_source_info_dict(source_info_dict: dict[str, Any]) -> list[Video]:
    """
    Get a list of `Video` objects from a source_info_dict.

    Parameters:
        source_info_dict (dict): The source_info_dict.

    Returns:
        list: The list of `Video` objects.
    """
    entries = source_info_dict["entries"]
    playlists = entries if entries[0].get("entries") else [entries]
    return [
        Video(
            title=video["title"],
            description=video["description"],
            url=video.get("webpage_url", video["url"]),
            released_at=datetime.strptime(video.get("upload_date"), "%Y%m%d")
            if video.get("upload_date")
            else None,
            media_url=None,
            media_filesize=None,
        )
        for playlist in playlists
        for video in playlist.get("entries", [])
    ]
