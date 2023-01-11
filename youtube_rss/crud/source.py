from typing import Any

from loguru import logger
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session

from youtube_rss.core.debug_helpers import timeit
from youtube_rss.crud.exceptions import RecordAlreadyExistsError
from youtube_rss.crud.video import VideoCRUD, refresh_videos
from youtube_rss.db.database import engine
from youtube_rss.models.source import Source, SourceCreate, SourceRead, generate_source_id_from_url
from youtube_rss.models.video import Video
from youtube_rss.services.feed import build_rss_file, delete_rss_file
from youtube_rss.services.source import (
    get_source_from_source_info_dict,
    get_source_info_dict,
    get_source_videos_from_source_info_dict,
)

from .base import BaseCRUD


class SourceCRUD(BaseCRUD[Source, SourceCreate, SourceRead]):
    def __init__(self, session: Session) -> None:
        super().__init__(model=Source, session=session)

    async def delete(self, *args: BinaryExpression[Any], **kwargs: Any) -> None:
        source_id = kwargs.get("id")
        if source_id:
            try:
                await delete_rss_file(source_id=source_id)
            except FileNotFoundError as e:
                logger.warning(e)
        return await super().delete(*args, **kwargs)

    async def create_source_from_url(self, url: str) -> Source:
        """Create a new source from a URL.

        Args:
            url: The URL to create the source from.

        Returns:
            The created source.

        Raises:
            RecordAlreadyExistsError: If a source already exists for the given URL.
        """
        source_id = await generate_source_id_from_url(url=url)

        # Check if the source already exists
        db_source = await self.get_or_none(id=source_id)
        if db_source:
            raise RecordAlreadyExistsError("Record already exists for url.")

        # Fetch source information from yt-dlp and create the source object
        source_info_dict = await get_source_info_dict(
            source_id=source_id,
            url=url,
            extract_flat=True,
        )
        source = await get_source_from_source_info_dict(source_info_dict=source_info_dict)

        # Save the source to the database
        db_source = await self.create(source)

        # Fetch video information from yt-dlp for new videos
        return await self.fetch_source(source_id=source_id)

    async def fetch_source(self, source_id: str) -> Source:
        """Fetch new data from yt-dlp for the source and update the source in the database.

        This function will also delete any videos that are no longer associated with the source.

        Args:
            source_id: The id of the source to fetch and update.

        Returns:
            The updated source.
        """
        db_source = await self.get(id=source_id)

        # Fetch source information from yt-dlp and create the source object
        source_info_dict = await get_source_info_dict(
            source_id=source_id,
            url=db_source.url,
            extract_flat=True,
        )
        source = await get_source_from_source_info_dict(source_info_dict=source_info_dict)
        db_source = await self.update(in_obj=SourceCreate(**source.dict()), id=source_id)

        # Update Source Videos from Fetched Videos
        # db_source = await self.get(id=source_id)
        fetched_videos = await get_source_videos_from_source_info_dict(
            source_info_dict=source_info_dict
        )

        added_videos = await add_new_source_videos_from_fetched_videos(
            fetched_videos=fetched_videos, db_source=db_source
        )

        # NOTE: Enable if db grows too large. Otherwise best not to delete any videos
        # from database as podcast app will still reference the video's feed_media_url
        # deleted_videos = await delete_orphaned_source_videos(
        #     fetched_videos=fetched_videos, db_source=db_source
        # )
        deleted_videos: list[Video] = []

        refreshed_videos = await refresh_videos(videos=db_source.videos)

        # Build RSS File
        await build_rss_file(source=db_source)

        logger.success(
            f"Completed fetching Source(id='{db_source.id}'). "
            f"[{len(added_videos)}/{len(deleted_videos)}/{len(refreshed_videos)}] "
            f"Added {len(added_videos)} new videos. "
            f"Deleted {len(deleted_videos)} orphaned videos. "
            f"Refreshed {len(refreshed_videos)} videos."
        )

        return await self.get(id=source_id)

    async def fetch_all_sources(self) -> list[Source]:
        """
        Fetch all sources.

        Returns:
            List[Source]: List of fetched sources
        """
        logger.warning("Fetching ALL Sources...")
        sources = await self.get_all() or []
        fetched = []
        for source in sources:
            fetched.append(await self.fetch_source(source_id=source.id))

        return fetched

    async def fetch_source_videos(self, source_id: str) -> Source:
        """Fetch new data from yt-dlp for each video in the source.

        Args:
            source_id: The ID of the source to fetch videos for.

        Returns:
            The source with the updated videos.
        """
        # Get the source from the database
        source = await self.get(id=source_id)

        # Fetch new data for each video in the source
        for video in source.videos:
            await video_crud.fetch_video(video_id=video.id)

        # Return the updated source
        return await self.get(id=source_id)


with Session(engine) as _session:
    source_crud = SourceCRUD(session=_session)
    video_crud = VideoCRUD(session=_session)


async def refresh_all_sources() -> list[Source]:
    """
    Fetches new data from yt-dlp for all Sources.

    Returns:
        The list of refreshed Sources.
    """
    sources = await source_crud.get_all() or []
    return await refresh_sources(sources=sources)


async def refresh_sources(sources: list[Source]) -> list[Source]:
    """
    Fetches new data from yt-dlp for each Source.

    Args:
        sources: The list of sources to refresh.

    Returns:
        The list of refreshed Sources.
    """
    return [await source_crud.fetch_source(source_id=source.id) for source in sources]


async def add_new_source_videos_from_fetched_videos(
    fetched_videos: list[Video], db_source: Source
) -> list[Video]:
    """
    Add new videos from a list of fetched videos to a source in the database.

    Args:
        fetched_videos: A list of Video objects fetched from a source.
        db_source: The Source object in the database to add the new videos to.

    Returns:
        A list of Video objects that were added to the database.
    """
    db_video_ids = [video.id for video in db_source.videos]

    # Add videos that were fetched, but not in the database.
    added_videos = []
    for fetched_video in fetched_videos:
        if fetched_video.id not in db_video_ids:
            added_videos.append(fetched_video)
            await video_crud.create(in_obj=fetched_video)

    return added_videos


async def delete_orphaned_source_videos(
    fetched_videos: list[Video], db_source: Source
) -> list[Video]:
    """
    Delete videos that are no longer present in `fetched_videos`.

    Args:
        fetched_videos: The list of Videos to compare the videos against.
        db_source: The source object in the database to delete videos from.

    Returns:
        The list of deleted Videos.
    """
    fetched_video_ids = [video.id for video in fetched_videos]

    # Iterate through the videos in the source in the database
    deleted_videos = []
    for db_video in db_source.videos:
        if db_video.id not in fetched_video_ids:
            deleted_videos.append(db_video)
            await video_crud.delete(id=db_video.id)

    return deleted_videos
