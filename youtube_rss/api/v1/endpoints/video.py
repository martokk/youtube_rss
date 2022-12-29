from typing import List

from fastapi import APIRouter, HTTPException, status

from youtube_rss.db.crud import video_crud
from youtube_rss.models.video import Video

router = APIRouter()
crud = video_crud


@router.get("/", response_model=List[Video], status_code=status.HTTP_200_OK)
async def get_all() -> List[Video]:
    """
    Get all items.
    """
    return crud.get_all()


@router.post("/", response_model=Video, status_code=status.HTTP_201_CREATED)
async def create(video: Video) -> Video:
    """
    Create new item.
    """
    return crud.create(video)


@router.get("/{video_id}", response_model=Video)
async def get(video_id: str) -> Video:
    """
    Get item by ID.
    """
    db_video = crud.get(video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found")
    return db_video


@router.patch("/{video_id}", response_model=Video)
async def update(video_id: str, video: Video) -> Video:
    """
    Update an item.
    """
    db_video = crud.get(video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found")
    update_data = video.dict()
    for field in video.dict():
        if field in update_data:
            setattr(db_video, field, update_data[field])
    crud.update(db_video)
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(video_id: str) -> bool:
    """
    Delete an item.
    """
    db_video = crud.get(video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found")
    return crud.delete(db_video)
