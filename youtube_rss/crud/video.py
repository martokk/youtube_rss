from datetime import datetime, timedelta

from loguru import logger
from sqlmodel import Session

from youtube_rss.config import MAX_VIDEO_AGE_HOURS
from youtube_rss.core.debug_helpers import timeit
from youtube_rss.crud.exceptions import RecordAlreadyExistsError
from youtube_rss.db.database import engine
from youtube_rss.models.video import Video, VideoCreate, VideoRead, generate_video_id_from_url
from youtube_rss.services.videos import get_video_from_video_info_dict, get_video_info_dict

from .base import BaseCRUD


class VideoCRUD(BaseCRUD[Video, VideoCreate, VideoRead]):
    def __init__(self, session: Session) -> None:
        super().__init__(model=Video, session=session)

    async def create_video_from_url(self, url: str, source_id: str) -> Video:
        """Create a new video from a URL.

        Args:
            url: The URL to create the video from.
            source_id: The id of the Source the video belongs to.

        Returns:
            The created video.

        Raises:
            RecordAlreadyExistsError: If a video already exists for the given URL.
        """
        video_id = await generate_video_id_from_url(url=url)

        # Check if the video already exists
        db_video = await self.get_or_none(id=video_id)
        if db_video:
            raise RecordAlreadyExistsError("Record already exists for url.")

        # Fetch video information from yt-dlp and create the video object
        video_info_dict = await get_video_info_dict(url=url)
        video = await get_video_from_video_info_dict(
            video_info_dict=video_info_dict, source_id=source_id
        )

        # Save the video to the database
        return await self.create(video)

    async def fetch_video(self, video_id: str) -> Video:
        """Fetches new data from yt-dlp for the video.

        Args:
            video_id: The ID of the video to fetch data for.

        Returns:
            The updated video.
        """
        # Get the video from the database
        db_video = await self.get(id=video_id)
        source_id = db_video.source_id

        # Fetch video information from yt-dlp and create the video object
        video_info_dict = await get_video_info_dict(url=db_video.url)
        video = await get_video_from_video_info_dict(
            video_info_dict=video_info_dict, source_id=source_id
        )

        # Update the video in the database and return it
        return await self.update(VideoCreate(**video.dict()), id=video.id)

    async def fetch_all_videos(self) -> list[Video]:
        """
        Fetch videos from all sources.

        Returns:
            List[Video]: List of fetched videos
        """
        logger.warning("Fetching ALL Videos...")
        videos = await self.get_all() or []
        fetched = []
        for video in videos:
            fetched.append(await self.fetch_video(video_id=video.id))

        return fetched


with Session(engine) as _session:
    video_crud = VideoCRUD(session=_session)


async def refresh_all_videos(older_than_hours: int) -> list[Video]:
    """
    Fetches new data from yt-dlp for all Videos that are older than a certain number of hours.

    Args:
        older_than_hours: The minimum age of the videos to refresh, in hours.

    Returns:
        The refreshed list of videos.
    """
    videos = await video_crud.get_all() or []
    return await refresh_videos(videos=videos, older_than_hours=older_than_hours)


async def fetch_videos(videos: list[Video]) -> list[Video]:
    """
    Fetches new data for a list of videos from yt-dlp.

    Args:
        videos: The list of videos to fetch.

    Returns:
        The fetched list of videos.
    """
    return [await video_crud.fetch_video(video_id=video.id) for video in videos]


@timeit
async def refresh_videos(
    videos: list[Video], older_than_hours: int = MAX_VIDEO_AGE_HOURS
) -> list[Video]:
    """
    Fetches new data from yt-dlp for videos that meet all criteria.

    Args:
        videos: The list of videos to refresh.
        older_than_hours: The minimum age of the videos to refresh, in hours.

    Returns:
        The refreshed list of videos.
    """
    age_threshold = datetime.utcnow() - timedelta(hours=older_than_hours)
    videos_needing_refresh = [
        video
        for video in videos
        if (
            video.updated_at < age_threshold or video.released_at is None or video.media_url is None
        )
    ]
    sorted_videos_needing_refresh = await sort_videos_by_updated_at(videos=videos_needing_refresh)
    return await fetch_videos(videos=sorted_videos_needing_refresh)


async def sort_videos_by_updated_at(videos: list[Video]) -> list[Video]:
    """
    Sorts a list of videos by the `updated_at` property.

    Args:
        videos: The list of videos to sort.

    Returns:
        The sorted list of videos.
    """
    return sorted(videos, key=lambda video: video.updated_at, reverse=False)


async def get_media_url_from_video_id(video_id: str) -> str:
    """
    Get the media URL for a video.

    Args:
        video_id: The id of the video to get the media URL for.

    Returns:
        The media URL for the video.

    Raises:
        ValueError: If the media URL for the video cannot be fetched.
    """
    video = await video_crud.get(id=video_id)
    if not video.media_url:
        video = await video_crud.fetch_video(video_id=video_id)
        if not video.media_url:
            raise ValueError("Unable to fetch media_url")
    return video.media_url
