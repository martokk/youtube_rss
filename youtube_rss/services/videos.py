from typing import Any

from youtube_rss.handlers import get_handler_from_url
from youtube_rss.models.video import Video
from youtube_rss.services.ytdlp import YDL_OPTS_BASE, get_info_dict


async def get_video_ydl_opts() -> dict[str, Any]:
    """
    Get the yt-dlp options for a video.

    Returns:
        dict: The yt-dlp options for the source.
    """
    return YDL_OPTS_BASE


async def get_video_info_dict(
    url: str,
) -> dict[str, Any]:
    """
    Retrieve the info_dict for a Video.

    This function first checks if a cached version of the info dictionary is available,
    and if it is, it returns that. Otherwise, it uses YouTube-DL to retrieve the
    info dictionary and then stores it in the cache for future use.

    Parameters:
        url (str): The URL of the video.


    Returns:
        dict: The info dictionary for the video.
    """
    # video_id = generate_video_id_from_url(url=url)
    # cache_file = Path(VIDEO_INFO_CACHE_PATH / f"{video_id}.pickle")

    # Load Cache
    # if use_cache and cache_file.exists():
    #     return pickle.loads(cache_file.read_bytes())

    # Get info_dict from yt-dlp
    ydl_opts = await get_video_ydl_opts()
    info_dict = await get_info_dict(url=url, ydl_opts=ydl_opts)

    # Save Pickle
    # cache_file.parent.mkdir(exist_ok=True, parents=True)
    # cache_file.write_bytes(pickle.dumps(info_dict))
    return info_dict


async def get_video_from_video_info_dict(video_info_dict: dict[str, Any], source_id: str) -> Video:
    handler = get_handler_from_url(url=video_info_dict["webpage_url"])
    video_dict = handler.map_video_info_dict_entity_to_video_dict(entry_info_dict=video_info_dict)
    video_dict["source_id"] = source_id
    return Video(**video_dict)
