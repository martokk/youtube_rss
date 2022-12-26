"""
This type stub file was generated by pyright.
"""

from .common import FileDownloader
from .external import FFmpegFD

class FFmpegSinkFD(FileDownloader):
    """ A sink to ffmpeg for downloading fragments in any form """
    def real_download(self, filename, info_dict): # -> tuple[Literal[True], Literal[False]] | tuple[Unknown, Literal[True]]:
        class FFmpegStdinFD(FFmpegFD):
            ...
        
        
    
    async def real_connection(self, sink, info_dict):
        """ Override this in subclasses """
        ...
    


class WebSocketFragmentFD(FFmpegSinkFD):
    async def real_connection(self, sink, info_dict):
        ...
    


