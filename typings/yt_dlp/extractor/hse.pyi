"""
This type stub file was generated by pyright.
"""

from .common import InfoExtractor

class HSEShowBaseInfoExtractor(InfoExtractor):
    _GEO_COUNTRIES = ...


class HSEShowIE(HSEShowBaseInfoExtractor):
    _VALID_URL = ...
    _TESTS = ...


class HSEProductIE(HSEShowBaseInfoExtractor):
    _VALID_URL = ...
    _TESTS = ...

