from typing import Any

import datetime

from dateutil import tz

from youtube_rss.config import BUILD_FEED_DATEAFTER, BUILD_FEED_RECENT_VIDEOS
from youtube_rss.handlers.extractors.rumble import CustomRumbleChannelIE, CustomRumbleEmbedIE
from youtube_rss.services.ytdlp import YDL_OPTS_BASE

from .base import ServiceHandler

# import re


class RumbleHandler(ServiceHandler):
    USE_PROXY = False
    MEDIA_URL_REFRESH_INTERVAL = 60 * 60 * 8  # 8 Hours
    DOMAINS = ["rumble.com"]
    YTDLP_CUSTOM_EXTRACTORS = [CustomRumbleChannelIE, CustomRumbleEmbedIE]
    YDL_OPT_ALLOWED_EXTRACTORS = ["CustomRumbleEmbed", "CustomRumbleChannel"]

    # def sanitize_video_url(self, url: str) -> str:
    #     """
    #     Sanitizes the url to a standard format

    #     Args:
    #         url: The URL to be sanitized

    #     Returns:
    #         The sanitized URL.
    #     """
    #     url = await self.force_watch_v_format(url=url)
    #     return await super().sanitize_video_url(url=url)

    # def force_watch_v_format(self, url: str) -> str:
    #     """
    #     Extracts the YouTube video ID from a URL and returns the URL
    #     formatted like `https://www.youtube.com/watch?v=VIDEO_ID`.

    #     Args:
    #         url: The URL of the YouTube video.

    #     Returns:
    #         The formatted URL.

    #     Raises:
    #         ValueError: If the URL is not a valid YouTube video URL.
    #     """
    #     match = re.search(r"(?<=shorts/).*", url)
    #     if match:
    #         video_id = match.group()
    #     else:
    #         match = re.search(r"(?<=watch\?v=).*", url)
    #         if match:
    #             video_id = match.group()
    #         else:
    #             raise ValueError("Invalid YouTube video URL")

    #     return f"https://www.youtube.com/watch?v={video_id}"

    def get_source_ydl_opts(self, extract_flat: bool) -> dict[str, Any]:
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
            "allowed_extractors": self.YDL_OPT_ALLOWED_EXTRACTORS,
        }

    def map_source_info_dict_to_source_dict(
        self, source_info_dict: dict[str, Any], source_videos: list[Any]
    ) -> dict[str, Any]:
        """
        Maps a 'source_info_dict' to a Source dictionary.

        Args:
            source_info_dict: A dictionary containing information about a source.
            source_videos: A list of Video objects that belong to the source.

        Returns:
            A Source object.
        """
        return {
            "url": source_info_dict["url"],
            "name": source_info_dict["title"],
            "author": source_info_dict["uploader"],
            "logo": source_info_dict["thumbnail"],
            "ordered_by": "release",
            "description": None,
            "videos": source_videos,
            "extractor": source_info_dict["extractor_key"],
        }

    def map_source_info_dict_entity_to_video_dict(
        self, source_id: str, entry_info_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Maps a video 'entry_info_dict' from a 'source_info_dict' (flat_extract) to a `Video` object.
        Use this when when `extract_flat=True` is used.

        Args:
            source_id: The id of the source the video belongs to.
            entry_info_dict: A dictionary containing information about the video.

        Returns:
            A `Video` dictionary created from the `entry_info_dict`.
        """
        url = entry_info_dict.get("webpage_url", entry_info_dict["url"])
        return {
            "source_id": source_id,
            "url": url,
            "added_at": datetime.datetime.now(tz=tz.tzutc()),
            "title": None,
            "description": None,
            "released_at": None,
            "media_url": None,
            "media_filesize": None,
        }

    def map_video_info_dict_entity_to_video_dict(
        self, entry_info_dict: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Maps a video 'entry_info_dict' from a 'video_info_dict' to a `Video` object.

        Args:
            entry_info_dict: A dictionary containing information about the video.

        Returns:
            A `Video` dictionary created from the `entry_info_dict`.
        """
        format_info_dict = self._get_format_info_dict_from_entry_info_dict(
            entry_info_dict=entry_info_dict, format_number=entry_info_dict["format_id"]
        )
        media_filesize = format_info_dict.get("filesize") or format_info_dict.get(
            "filesize_approx", 0
        )
        released_at = datetime.datetime.utcfromtimestamp(entry_info_dict["timestamp"])
        return {
            "title": entry_info_dict["title"],
            "uploader": entry_info_dict["uploader"],
            "uploader_id": entry_info_dict["uploader"],
            "description": None,
            "duration": entry_info_dict["duration"],
            "url": entry_info_dict["original_url"],
            "media_url": format_info_dict["url"],
            "media_filesize": media_filesize,
            "thumbnail": entry_info_dict["thumbnail"],
            "released_at": released_at,
        }

    def _get_format_info_dict_from_entry_info_dict(
        self, entry_info_dict: dict[str, Any], format_number: int | str
    ) -> dict[str, Any]:
        """
        Returns the dictionary from entry_info_dict['formats'] that has a 'format_id' value
        matching format_number.

        Args:
            entry_info_dict: The entity dictionary returned by youtube_dl.YoutubeDL.extract_info.
            format_number: The 'format_id' value to search for in entry_info_dict['formats'].

        Returns:
            The dictionary from entry_info_dict['formats'] that has a 'format_id'
                value matching format_number.

        Raises:
            ValueError: If no dictionary in entry_info_dict['formats'] has a 'format_id'
                value matching format_number.
        """
        try:
            return next(
                (
                    format_dict
                    for format_dict in entry_info_dict["formats"]
                    if format_dict["format_id"] == str(format_number)
                )
            )
        except StopIteration as exc:
            raise ValueError(
                f"Format '{str(format_number)}' was not found in the entry_info_dict['formats']."
            ) from exc
