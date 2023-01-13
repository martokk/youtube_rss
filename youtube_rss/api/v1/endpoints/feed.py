from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse

from youtube_rss.api.v1.deps import authenticated_user
from youtube_rss.crud.exceptions import RecordNotFoundError
from youtube_rss.crud.source import source_crud
from youtube_rss.services.feed import build_rss_file, delete_rss_file, get_rss_file

router = APIRouter()


@router.get("/{source_id}", response_class=HTMLResponse)
async def get_rss(source_id: str) -> Response:
    """
    Gets a rss file for source_id and returns it as a Response
    """
    try:
        rss_file = await get_rss_file(source_id=source_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc

    # Serve RSS File as a Response
    content = rss_file.read_text()
    return Response(content)


@router.put("/{source_id}", response_class=HTMLResponse)
async def build_rss(source_id: str, _=Depends(authenticated_user())) -> Response:
    """
    Builds a new rss file for source_id and returns it as a Response.
    """
    try:
        source = await source_crud.get(id=source_id)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc

    try:
        rss_file = await build_rss_file(source=source)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc

    # Serve RSS File as a Response
    content = rss_file.read_text()
    return Response(content)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rss(source_id: str, _=Depends(authenticated_user())) -> None:
    """
    Deletes the .rss file for a feed.
    """
    try:
        source = await source_crud.get(id=source_id)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args) from exc
    return await delete_rss_file(source_id=source.id)
