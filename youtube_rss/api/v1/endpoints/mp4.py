from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from youtube_rss.core.proxy import reverse_proxy
from youtube_rss.crud.video import video_crud

router = APIRouter()


@router.get("/{video_id}")
@router.head("/{video_id}")
async def reverse_proxy_video_id(video_id: str, request: Request) -> StreamingResponse:
    """
    Streams the response of yt-dlp
    """
    video = await video_crud.get(id=video_id)
    if video.media_url is None:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="The server has not yet retrieved a media_url from yt-dlp.",
        )
    return await reverse_proxy(url=video.media_url, request=request)
