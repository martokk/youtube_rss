from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse, Response

from youtube_rss.core.log import logger
from youtube_rss.core.proxy import reverse_proxy
from youtube_rss.crud.exceptions import RecordNotFoundError
from youtube_rss.crud.video import video_crud
from youtube_rss.handlers import get_handler_from_string

router = APIRouter()


@router.get("/{video_id}")
@router.head("/{video_id}")
async def handle_media(video_id: str, request: Request) -> Response:
    """
    Handles the repose for a media request by video_id.
    Uses a reverse proxy if required by the handler.
    """
    try:
        video = await video_crud.get(id=video_id)
    except RecordNotFoundError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The video_id '{video_id}' was not found.",
        ) from e

    if video.media_url is None:
        logger.error("The server has not yet retrieved a media_url from yt-dlp.")
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="The server has not yet retrieved a media_url from yt-dlp.",
        )
    handler = get_handler_from_string(handler_string=video.handler)
    if handler.USE_PROXY:
        return await reverse_proxy(url=video.media_url, request=request)
    return RedirectResponse(url=video.media_url)
