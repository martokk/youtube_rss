from typing import Any

from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from loguru import logger
from yt_dlp import YoutubeDL

from youtube_rss.core.proxy import reverse_proxy

YDL_OPTS_BASE: dict[str, Any] = {
    "logger": logger,
    "format": "worst[ext=mp4]",
    "skip_download": True,
    "simulate": True,
    "verbose": True,
}


async def get_info_dict(
    url: str, ydl_opts: dict[str, Any], ie_key: str | None = None
) -> dict[str, Any]:
    """
    Use YouTube-DL to get the info dictionary for a given URL.

    Parameters:
        url (str): The URL of the object to retrieve info for.
        ydl_opts (dict[str, Any]): The options to use with YouTube-DL.
        ie_key (Optional[str]): The name of the YouTube-DL info extractor to use.
            If not provided, the default extractor will be used.

    Returns:
        dict[str, Any]: The info dictionary for the object.

    Raises:
        ValueError: If the info dictionary could not be retrieved.
    """
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False, ie_key=ie_key)
        info_dict["url"] = url

    if info_dict is None:
        raise ValueError(
            f"yt-dlp did not download a info_dict object. {info_dict=} {url=} {ydl_opts=}"
        )
    return info_dict


async def get_direct_download_url(url: str) -> str:
    """
    Get the direct download URL for a video.

    Parameters:
        url (str): The URL of the video.

    Returns:
        str: The direct download URL for the video.
    """
    info_dict = await get_info_dict(
        url=url,
        ydl_opts=YDL_OPTS_BASE,
    )
    return info_dict["url"]


async def get_direct_download_url_from_extractor_video_id(extractor: str, video_id: str) -> str:
    """
    Get the direct download URL for a video using a specific YouTube-DL extractor.

    Parameters:
        extractor (str): The name of the YouTube-DL extractor to use.
        video_id (str): The ID of the video.

    Returns:
        str: The direct download URL for the video.
    """
    info_dict = await get_info_dict(
        url=video_id,
        ydl_opts=YDL_OPTS_BASE,
        ie_key=extractor,
    )
    return info_dict["url"]


async def ytdlp_reverse_proxy(extractor: str, video_id: str, request: Request) -> StreamingResponse:
    """
    Streams the video_id's direct download url via a reverse proxy.

    Parameters:
        extractor (str): The name of the YouTube-DL extractor to use.
        video_id (str): The ID of the video.
        request (Request): The incoming HTTP request.

    Returns:
        StreamingResponse: A streaming response that plays the video.
    """
    direct_download_url = await get_direct_download_url_from_extractor_video_id(
        extractor=extractor, video_id=video_id
    )

    return await reverse_proxy(url=direct_download_url, request=request)
