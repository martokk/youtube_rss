from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from youtube_rss import crud
from youtube_rss.api.deps import authenticated_user, get_active_user_id, get_db
from youtube_rss.models.source import Source, SourceCreate, SourceRead

ModelClass = Source
ModelReadClass = SourceRead
ModelCreateClass = SourceCreate

router = APIRouter()


@router.post("/", response_model=ModelReadClass, status_code=status.HTTP_201_CREATED)
async def create(
    in_obj: ModelCreateClass,
    db=Depends(get_db),
    user_id: str = Depends(get_active_user_id()),
) -> ModelClass:
    """
    Create a new item.
    """
    try:
        return await crud.source.create_source_from_url(url=in_obj.url, user_id=user_id, db=db)
    except crud.RecordAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Source already exists") from exc


@router.get("/{id}", response_model=ModelReadClass)
async def get(
    id: str, db=Depends(get_db), _: Any = Depends(authenticated_user())
) -> ModelClass | None:
    """
    Get an item.
    """
    try:
        return await crud.source.get(id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.get("/", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def get_all(
    db=Depends(get_db), _: Any = Depends(authenticated_user())
) -> list[ModelClass] | None:
    """
    Get all items.
    """
    return await crud.source.get_all(db=db)


@router.patch("/{id}", response_model=ModelReadClass)
async def update(
    id: str,
    in_obj: ModelCreateClass,
    db=Depends(get_db),
    _: Any = Depends(authenticated_user()),
) -> ModelClass:
    """
    Update an item.
    """
    try:
        return await crud.source.update(in_obj, id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: str, db=Depends(get_db), _: Any = Depends(authenticated_user())) -> None:
    """
    Delete an item.
    """
    try:
        return await crud.source.delete(id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.put("/{source_id}/fetch", response_model=SourceRead)
async def fetch_source(
    source_id: str, db=Depends(get_db), _: Any = Depends(authenticated_user())
) -> Source:
    """
    Fetches new data from yt-dlp and updates a source on the server.

    Args:
        source_id: The ID of the source to update.

    Returns:
        The updated source.

    Raises:
        HTTPException: If the source was not found.
    """
    try:
        return await crud.source.fetch_source(source_id=source_id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.put("/fetch", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def fetch_all(
    db=Depends(get_db), _: Any = Depends(authenticated_user())
) -> list[ModelClass] | None:
    """
    Fetch all sources.
    """
    return await crud.source.fetch_all_sources(db=db)
