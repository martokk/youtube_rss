from typing import Any

from youtube_rss.handlers import get_handler_from_url
from youtube_rss.models.source import Source
from youtube_rss.models.video import Video
from youtube_rss.services.ytdlp import get_info_dict


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
    handler = get_handler_from_url(url=url)
    ydl_opts = handler.get_source_ydl_opts(extract_flat=extract_flat)
    custom_extractors = handler.YTDLP_CUSTOM_EXTRACTORS or []
    _source_info_dict = await get_info_dict(
        url=url,
        ydl_opts=ydl_opts,
        custom_extractors=custom_extractors,
        # ie_key="CustomRumbleChannel",
    )
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
    handler = get_handler_from_url(url=source_info_dict["metadata"]["url"])
    source_videos = await get_source_videos_from_source_info_dict(source_info_dict=source_info_dict)
    return Source(
        **handler.map_source_info_dict_to_source_dict(
            source_info_dict=source_info_dict, source_videos=source_videos
        )
    )


async def get_source_videos_from_source_info_dict(source_info_dict: dict[str, Any]) -> list[Video]:
    """
    Get a list of `Video` objects from a source_info_dict.

    Parameters:
        source_info_dict (dict): The source_info_dict.

    Returns:
        list: The list of `Video` objects.
    """
    handler = get_handler_from_url(url=source_info_dict["metadata"]["url"])
    entries = source_info_dict["entries"]
    playlists = entries if entries[0].get("entries") else [source_info_dict]
    video_dicts = [
        handler.map_source_info_dict_entity_to_video_dict(
            source_id=source_info_dict["source_id"], entry_info_dict=entry_info_dict
        )
        for playlist in playlists
        for entry_info_dict in playlist.get("entries", [])
    ]
    videos = [Video(**video_dict) for video_dict in video_dicts]
    return videos
