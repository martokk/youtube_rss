from fastapi import APIRouter, HTTPException, status

from youtube_rss.crud.exceptions import RecordAlreadyExistsError, RecordNotFoundError
from youtube_rss.crud.source import source_crud
from youtube_rss.models.source import Source, SourceCreate, SourceRead

router = APIRouter()
crud = source_crud


router = APIRouter()
crud = source_crud
ModelClass = Source
ModelReadClass = SourceRead
ModelCreateClass = SourceCreate


@router.post("/", response_model=ModelReadClass, status_code=status.HTTP_201_CREATED)
async def create(in_obj: ModelCreateClass) -> ModelClass:
    """
    Create a new item.
    """
    try:
        return await crud.create_source_from_url(url=in_obj.url)
    except RecordAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Source already exists") from exc


@router.get("/{id}", response_model=ModelReadClass)
async def get(id: str) -> ModelClass | None:
    """
    Get an item.
    """
    try:
        return await crud.get(id=id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.get("/", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def get_all() -> list[ModelClass] | None:
    """
    Get all items.
    """
    return await crud.get_all()


@router.patch("/{id}", response_model=ModelReadClass)
async def update(id: str, in_obj: ModelCreateClass) -> ModelClass:
    """
    Update an item.
    """
    try:
        return await crud.update(in_obj, id=id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: str) -> None:
    """
    Delete an item.
    """
    try:
        return await crud.delete(id=id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.put("/{source_id}/fetch", response_model=SourceRead)
async def fetch_source(source_id: str) -> Source:
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
        return await source_crud.fetch_source(source_id=source_id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source Not Found"
        ) from exc


@router.put("/fetch", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def fetch_all() -> list[ModelClass] | None:
    """
    Fetch all sources.
    """
    return await source_crud.fetch_all_sources()
