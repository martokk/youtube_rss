import re

from .base import ServiceHandler


class YoutubeHandler(ServiceHandler):
    USE_PROXY = True
    MEDIA_URL_REFRESH_INTERVAL = 60 * 60 * 8  # 8 Hours

    def sanitize_video_url(self, url: str) -> str:
        """
        Sanitizes the url to a standard format

        Args:
            url: The URL to be sanitized

        Returns:
            The sanitized URL.
        """
        url = self.force_watch_v_format(url=url)
        return super().sanitize_video_url(url=url)

    def force_watch_v_format(self, url: str) -> str:
        """
        Extracts the YouTube video ID from a URL and returns the URL
        formatted like `https://www.youtube.com/watch?v=VIDEO_ID`.

        Args:
            url: The URL of the YouTube video.

        Returns:
            The formatted URL.

        Raises:
            ValueError: If the URL is not a valid YouTube video URL.
        """
        match = re.search(r"(?<=shorts/).*", url)
        if match:
            video_id = match.group()
        else:
            match = re.search(r"(?<=watch\?v=).*", url)
            if match:
                video_id = match.group()
            else:
                raise ValueError("Invalid YouTube video URL")

        return f"https://www.youtube.com/watch?v={video_id}"
