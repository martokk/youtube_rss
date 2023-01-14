from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from youtube_rss import crud, settings
from youtube_rss.api.deps import get_db

router = APIRouter()
templates = Jinja2Templates(directory="youtube_rss/views/templates")


@router.get(
    "/u/{username}", summary="Returns HTML Reponse with list of feeds", response_class=HTMLResponse
)
async def read_root(request: Request, username: str, db: Session = Depends(get_db)) -> Response:
    """
    Server root. Returns html response of all sources.

    Args:
        request(Request): The request object
        username: The username to display

    Returns:
        Response: HTML page with list of sources

    Raises:
        HTTPException: User not found
    """
    try:
        user = await crud.user.get(username=username, db=db)
    except crud.RecordNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e
    # sources = await source_crud.get_many(created_by=user.id)
    sources_context = [
        {
            "name": source.name,
            "url": source.url,
            "pktc_subscription_url": f"pktc://subscribe/{settings.base_domain}{source.feed_url}",
        }
        for source in user.sources
    ]
    context = {"request": request, "sources": sources_context, "username": username}
    return templates.TemplateResponse("home.html", context)
