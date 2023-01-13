from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from youtube_rss.config import BASE_DOMAIN
from youtube_rss.crud.exceptions import RecordNotFoundError
from youtube_rss.crud.user import user_crud

router = APIRouter()
templates = Jinja2Templates(directory="youtube_rss/views/templates")


@router.get(
    "/u/{username}", summary="Returns HTML Reponse with list of feeds", response_class=HTMLResponse
)
async def read_root(request: Request, username: str) -> Response:
    """
    Server root. Returns html response of all sources.

    Returns:
        Response: HTML page with list of sources
    """
    try:
        user = await user_crud.get(username=username)
    except RecordNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    # sources = await source_crud.get_many(created_by=user.id)
    sources_context = [
        {
            "name": source.name,
            "url": source.url,
            "pktc_subscription_url": f"pktc://subscribe/{BASE_DOMAIN}{source.feed_url}",
        }
        for source in user.sources
    ]
    context = {"request": request, "sources": sources_context, "username": username}
    return templates.TemplateResponse("home.html", context)
