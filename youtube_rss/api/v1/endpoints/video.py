from fastapi import APIRouter, HTTPException, status

from youtube_rss.crud.exceptions import RecordAlreadyExistsError, RecordNotFoundError
from youtube_rss.crud.video import video_crud
from youtube_rss.models.video import Video, VideoCreate, VideoRead

router = APIRouter()
crud = video_crud
ModelClass = Video
ModelReadClass = VideoRead
ModelCreateClass = VideoCreate


@router.post("/", response_model=ModelReadClass, status_code=status.HTTP_201_CREATED)
async def create(in_obj: ModelCreateClass) -> ModelClass:
    """
    Create a new item.
    """
    try:
        return await crud.create_video_from_url(url=in_obj.url, source_id=in_obj.source_id)
    except RecordAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Video already exists") from exc


@router.get("/{id}", response_model=ModelReadClass)
async def get(id: str) -> ModelClass | None:
    """
    Get an item.
    """
    try:
        return await crud.get(id=id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.put("/{id}/fetch", response_model=VideoRead)
async def fetch_video(id: str) -> Video:
    """
    Fetches new data from yt-dlp and updates a video on the server.

    Args:
        video_id: The ID of the video to update.

    Returns:
        The updated video.

    Raises:
        HTTPException: If the video was not found.
    """
    try:
        return await video_crud.fetch_video(video_id=id)
    except RecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Video Not Found"
        ) from exc


@router.put("/fetch", response_model=list[ModelReadClass], status_code=status.HTTP_200_OK)
async def fetch_all() -> list[ModelClass] | None:
    """
    Fetch all Videos.
    """
    return await video_crud.fetch_all_videos()
