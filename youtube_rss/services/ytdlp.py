from typing import Any

from fastapi.responses import StreamingResponse
from loguru import logger
from yt_dlp import YoutubeDL
from yt_dlp.extractor.youtube import YoutubeIE

from youtube_rss.core.proxy import reverse_proxy

YDL_OPTS_DIRECT_DOWNLOAD_URL = {
    "logger": logger,
    "outtmpl": "%(title)s%(ext)s",
    "format": "b",
    "skip_download": True,
}


def get_info_dict(url: str, ydl_opts: dict[str, Any], ie_key=None) -> dict[str, Any]:
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False, ie_key=ie_key)

    if info_dict is None:
        raise ValueError(
            f"yt-dlp did not download a info_dict object. {info_dict=} {url=} {ydl_opts=}"
        )
    return info_dict


def get_direct_download_url(url: str) -> str:
    """
    Gets the direct download url from a video_id
    """
    # print(video_id)
    # url = "http://www.example.com"
    # return url

    info_dict = get_info_dict(
        url=url,
        ydl_opts={
            "logger": logger,
            "outtmpl": "%(title)s%(ext)s",
            "format": "b",
            "skip_download": True,
        },
    )

    return info_dict["url"]


def get_direct_download_url_from_extractor_video_id(extractor: str, video_id: str) -> str:
    """
    Gets the direct download url from a extractor and video_id
    """
    info_dict = get_info_dict(
        url=video_id,
        ie_key=extractor,
        ydl_opts={
            "logger": logger,
            "outtmpl": "%(title)s%(ext)s",
            "format": "b",
            "skip_download": True,
            "simulate": True,
        },
    )

    return info_dict["url"]


async def ytdlp_reverse_proxy(extractor: str, video_id: str) -> StreamingResponse:
    """
    Streams the video_id's direct download url via a reverse proxy.
    """
    direct_download_url = get_direct_download_url_from_extractor_video_id(
        extractor=extractor, video_id=video_id
    )

    return await reverse_proxy(url=direct_download_url)
