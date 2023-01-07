from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response

from youtube_rss.core.proxy import reverse_proxy
from youtube_rss.crud.video import video_crud
from youtube_rss.handlers import get_handler_from_string

router = APIRouter()


@router.get("/{video_id}")
@router.head("/{video_id}")
async def reverse_proxy_video_id(video_id: str, request: Request) -> Response:
    """
    Streams the response of yt-dlp
    """
    video = await video_crud.get(id=video_id)
    if video.media_url is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="The server has not yet retrieved a media_url from yt-dlp.",
        )
    handler = get_handler_from_string(handler_string=video.handler)
    if handler.USE_PROXY:
        return await reverse_proxy(url=video.media_url, request=request)
    return RedirectResponse(url=video.media_url)
