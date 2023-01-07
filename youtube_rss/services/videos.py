from typing import Any

from datetime import datetime, timezone

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


async def get_video_from_video_info_dict(video_info_dict: dict[str, Any]) -> Video:
    format_info_dict = await get_format_info_dict_from_video_info_dict(
        video_info_dict=video_info_dict, format_number=video_info_dict["format_id"]
    )
    media_filesize = format_info_dict.get("filesize") or format_info_dict.get("filesize_approx", 0)
    if not media_filesize:
        print(f"{format_info_dict.get('filesize')=} - {format_info_dict.get('filesize_approx')=}")
    released_at = datetime.strptime(video_info_dict["upload_date"], "%Y%m%d").replace(
        tzinfo=timezone.utc
    )
    return Video(
        title=video_info_dict["title"],
        uploader=video_info_dict["uploader"],
        uploader_id=video_info_dict["uploader_id"],
        description=video_info_dict["description"],
        duration=video_info_dict["duration"],
        url=video_info_dict["webpage_url"],
        media_url=format_info_dict["url"],
        media_filesize=media_filesize,
        thumbnail=video_info_dict["thumbnail"],
        released_at=released_at,
    )


async def get_format_info_dict_from_video_info_dict(
    video_info_dict: dict[str, Any], format_number: int | str
) -> dict[str, Any]:
    """
    Returns the dictionary from video_info_dict['formats'] that has a 'format_id' value
    matching format_number.

    Args:
        video_info_dict: The dictionary returned by youtube_dl.YoutubeDL.extract_info.
        format_number: The 'format_id' value to search for in video_info_dict['formats'].

    Returns:
        The dictionary from video_info_dict['formats'] that has a 'format_id'
            value matching format_number.

    Raises:
        ValueError: If no dictionary in video_info_dict['formats'] has a 'format_id'
            value matching format_number.
    """
    try:
        return next(
            (
                format_dict
                for format_dict in video_info_dict["formats"]
                if format_dict["format_id"] == str(format_number)
            )
        )
    except StopIteration as exc:
        raise ValueError(
            f"Format '{str(format_number)}' was not found in the video_info_dict['formats']."
        ) from exc
