from typing import Any

import datetime

from dateutil import tz

from youtube_rss.config import BUILD_FEED_DATEAFTER, BUILD_FEED_RECENT_VIDEOS
from youtube_rss.models.source import Source, SourceOrderBy
from youtube_rss.models.video import Video
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


async def get_source_info_dict(
    source_id: str | None,
    url: str,
    extract_flat: bool,
) -> dict[str, Any]:
    """
    Retrieve the info_dict from yt-dlp for a Source

    Parameters:
        source_id (Union[str, None]): An optional ID for the source. If not provided,
            a unique ID will be generated from the URL.
        url (str): The URL of the Source
        extract_flat (bool): Whether to extract a flat list of videos in the playlist.


    Returns:
        dict: The info dictionary for the Source

    """
    # source_id = source_id or await generate_source_id_from_url(url=url)
    # cache_file = Path(SOURCE_INFO_CACHE_PATH / source_id)

    # # Load Cache
    # if use_cache and cache_file.exists():
    #     return pickle.loads(cache_file.read_bytes())

    # Get info_dict from yt-dlp
    ydl_opts = await get_source_ydl_opts(extract_flat=extract_flat)
    _source_info_dict = await get_info_dict(url=url, ydl_opts=ydl_opts)
    _source_info_dict["source_id"] = source_id

    # Save Pickle
    # cache_file.write_bytes(pickle.dumps(_source_info_dict))
    return _source_info_dict


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
            source_id=source_info_dict["source_id"],
            title=video["title"],
            description=video["description"],
            url=video.get("webpage_url", video["url"]),
            released_at=datetime.datetime.strptime(video.get("upload_date"), "%Y%m%d").replace(
                tzinfo=tz.tzutc()
            )
            if video.get("upload_date")
            else None,
            media_url=None,
            media_filesize=None,
            added_at=datetime.datetime.now(tz=tz.tzutc()),
        )
        for playlist in playlists
        for video in playlist.get("entries", [])
    ]
