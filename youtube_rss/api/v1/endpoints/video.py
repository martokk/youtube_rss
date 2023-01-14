from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from youtube_rss import crud
from youtube_rss.api.deps import authenticated_user, get_db
from youtube_rss.models.video import Video, VideoCreate, VideoRead

ModelClass = Video
ModelReadClass = VideoRead
ModelCreateClass = VideoCreate

router = APIRouter()


@router.post("/", response_model=ModelReadClass, status_code=status.HTTP_201_CREATED)
async def create(
    in_obj: ModelCreateClass,
    db: Session = Depends(get_db),
    _: Any = Depends(authenticated_user()),
) -> ModelClass:
    """
    Create a new item.
    """
    try:
        return await crud.video.create_video_from_url(
            url=in_obj.url, source_id=in_obj.source_id, db=db
        )
    except crud.RecordAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Video already exists") from exc


@router.get("/{id}", response_model=ModelReadClass)
async def get(
    id: str, db: Session = Depends(get_db), _: Any = Depends(authenticated_user())
) -> ModelClass | None:
    """
    Get an item.
    """
    try:
        return await crud.video.get(id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.get("/", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def get_all(
    db: Session = Depends(get_db), _: Any = Depends(authenticated_user())
) -> list[ModelClass] | None:
    """
    Get all items.
    """
    return await crud.video.get_all(db=db)


@router.patch("/{id}", response_model=ModelReadClass)
async def update(
    id: str,
    in_obj: ModelCreateClass,
    db: Session = Depends(get_db),
    _: Any = Depends(authenticated_user()),
) -> ModelClass:
    """
    Update an item.
    """
    try:
        return await crud.video.update(in_obj, id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: str, db: Session = Depends(get_db), _: Any = Depends(authenticated_user())
) -> None:
    """
    Delete an item.
    """
    try:
        return await crud.video.delete(id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.put("/{id}/fetch", response_model=VideoRead)
async def fetch_video(
    id: str, db: Session = Depends(get_db), _: Any = Depends(authenticated_user())
) -> Video:
    """
    Fetches new data from yt-dlp and updates a video on the server.

    Args:
        id: The ID of the video to update.
        db (Session, optional): The database session.

    Returns:
        The updated video.

    Raises:
        HTTPException: If the video was not found.
    """
    try:
        return await crud.video.fetch_video(video_id=id, db=db)
    except crud.RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.put("/fetch", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def fetch_all(
    db: Session = Depends(get_db), _: Any = Depends(authenticated_user())
) -> list[ModelClass] | None:
    """
    Fetch all Videos.
    """
    return await crud.video.fetch_all_videos(db=db)
