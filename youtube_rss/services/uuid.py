from urllib.parse import ParseResult, urlparse

import shortuuid


def generate_uuid_from_url(url: str | ParseResult) -> str:
    """
    Sanitized url, then generates a uuid from url. Return first 8 chars of uuid.
    """
    parse_result = urlparse(url) if isinstance(url, str) else url
    sanitized_url = parse_result.geturl()
    return shortuuid.uuid(sanitized_url)[:8]
