from urllib.parse import ParseResult, urlparse

from .base import ServiceHandler
from .youtube import YoutubeHandler

# def get_handler_from_extractor(extractor: str) -> ServiceHandler:
#     if extractor == "YoutubeTab":
#         return YoutubeHandler()
#     return ServiceHandler()


def get_handler_from_url(url: str | ParseResult) -> ServiceHandler:
    url = url if isinstance(url, ParseResult) else urlparse(url=url)

    if url.hostname == "www.youtube.com":
        return YoutubeHandler()
    return ServiceHandler()


def get_handler_from_handler_string(handler_string: str) -> ServiceHandler:
    handler_cls = globals()[handler_string]
    return handler_cls()
