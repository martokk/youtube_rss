from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import HTMLResponse

from youtube_rss.services.feed import build_rss_file, get_rss_file

router = APIRouter()


@router.get("/{feed_id}", response_class=HTMLResponse)
async def get(feed_id: str):
    """
    Gets a rss file for feed_id and returns it as a Response
    """
    try:
        rss_file = get_rss_file(feed_id=feed_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc

    # Serve RSS File as a Response
    content = rss_file.read_text()
    return Response(content)


@router.put("/{feed_id}", response_class=HTMLResponse)
async def update(feed_id: str):
    """
    Builds a new rss file for feed_id and returns it as a Response.
    """
    try:
        rss_file = build_rss_file(feed_id=feed_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc

    # Serve RSS File as a Response
    content = rss_file.read_text()
    return Response(content)
