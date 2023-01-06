from urllib.parse import urlparse


class ServiceHandler:
    USE_PROXY = False
    MEDIA_URL_EXPIRY_INTERVAL = 60 * 60 * 24 * 365  # 1 Year

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def sanitize_url(self, url: str) -> str:
        """
        Sanitizes the url to a standard format

        Args:
            url: The URL to be sanitized

        Returns:
            The sanitized URL.
        """
        parsed_url = urlparse(url)
        return parsed_url.geturl()

    def sanitize_source_url(self, url: str) -> str:
        """
        Sanitizes the Source url to a standard format

        Args:
            url: The URL to be sanitized

        Returns:
            The sanitized URL.
        """
        return self.sanitize_url(url=url)

    def sanitize_video_url(self, url: str) -> str:
        """
        Sanitizes the Source url to a standard format

        Args:
            url: The URL to be sanitized

        Returns:
            The sanitized URL.
        """
        return self.sanitize_url(url=url)
