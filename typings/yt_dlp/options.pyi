"""
This type stub file was generated by pyright.
"""

import optparse

def parseOpts(overrideArguments=..., ignore_config_files=...):
    ...

class _YoutubeDLHelpFormatter(optparse.IndentedHelpFormatter):
    def __init__(self) -> None:
        ...
    
    @staticmethod
    def format_option_strings(option): # -> str:
        """ ('-o', '--option') -> -o, --format METAVAR """
        ...
    


class _YoutubeDLOptionParser(optparse.OptionParser):
    ALIAS_DEST = ...
    ALIAS_TRIGGER_LIMIT = ...
    def __init__(self) -> None:
        ...
    
    _UNKNOWN_OPTION = ...
    _BAD_OPTION = optparse.OptionValueError
    def parse_known_args(self, args=..., values=..., strict=...): # -> tuple[Values, list[str]]:
        """Same as parse_args, but ignore unknown switches. Similar to argparse.parse_known_args"""
        ...
    
    def error(self, msg):
        ...
    


def create_parser(): # -> _YoutubeDLOptionParser:
    ...

