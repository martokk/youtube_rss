from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from youtube_rss.services.ytdlp import ytdlp_reverse_proxy

router = APIRouter()


@router.get("/{extractor}/{video_id}")
async def reverse_proxy_video_id(
    extractor: str, video_id: str, request: Request
) -> StreamingResponse:
    """
    Streams the response of yt-dlp
    """
    return await ytdlp_reverse_proxy(extractor=extractor, video_id=video_id, request=request)


@router.head("/{extractor}/{video_id}")
async def reverse_proxy_video_id_head(
    extractor: str, video_id: str, request: Request
) -> StreamingResponse:
    """
    Streams the response of yt-dlp
    """
    return await ytdlp_reverse_proxy(extractor=extractor, video_id=video_id, request=request)
