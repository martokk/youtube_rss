from typing import Any

# from fastapi import Depends
from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import Session

from youtube_rss import crud
from youtube_rss.core.logger import logger
from youtube_rss.crud.exceptions import RecordAlreadyExistsError
from youtube_rss.models.source import (
    Source,
    SourceCreate,
    SourceUpdate,
    generate_source_id_from_url,
)
from youtube_rss.models.video import Video
from youtube_rss.services.feed import build_rss_file, delete_rss_file
from youtube_rss.services.source import (
    add_new_source_videos_from_fetched_videos,
    get_source_from_source_info_dict,
    get_source_info_dict,
    get_source_videos_from_source_info_dict,
)
from youtube_rss.services.videos import refresh_videos

from .base import BaseCRUD


class SourceCRUD(BaseCRUD[Source, SourceCreate, SourceUpdate]):
    async def delete(self, db: Session, *args: BinaryExpression[Any], **kwargs: Any) -> None:
        source_id = kwargs.get("id")
        if source_id:
            try:
                await delete_rss_file(source_id=source_id)
            except FileNotFoundError as e:
                logger.warning(e)
        return await super().delete(db=db, *args, **kwargs)

    async def create_source_from_url(self, db: Session, url: str, user_id: str) -> Source:
        """Create a new source from a URL.

        Args:
            url: The URL to create the source from.
            user_id(str): The user id
            db (Session): The database session.

        Returns:
            The created source.

        Raises:
            RecordAlreadyExistsError: If a source already exists for the given URL.
        """
        source_id = await generate_source_id_from_url(url=url)

        # Check if the source already exists
        db_source = await self.get_or_none(id=source_id, db=db)
        if db_source:
            raise RecordAlreadyExistsError("Record already exists for url.")

        # Fetch source information from yt-dlp and create the source object
        source_info_dict = await get_source_info_dict(
            source_id=source_id,
            url=url,
            extract_flat=True,
        )
        _source = await get_source_from_source_info_dict(
            source_info_dict=source_info_dict, user_id=user_id
        )

        # Save the source to the database
        db_source = await self.create(in_obj=_source, db=db)

        # Fetch video information from yt-dlp for new videos
        return await self.fetch_source(source_id=source_id, db=db)

    async def fetch_source(self, db: Session, source_id: str) -> Source:
        """Fetch new data from yt-dlp for the source and update the source in the database.

        This function will also delete any videos that are no longer associated with the source.

        Args:
            source_id: The id of the source to fetch and update.
            db (Session): The database session.

        Returns:
            The updated source.
        """
        db_source = await self.get(id=source_id, db=db)

        # Fetch source information from yt-dlp and create the source object
        source_info_dict = await get_source_info_dict(
            source_id=source_id,
            url=db_source.url,
            extract_flat=True,
        )
        _source = await get_source_from_source_info_dict(
            source_info_dict=source_info_dict, user_id=db_source.created_by
        )
        db_source = await self.update(in_obj=SourceCreate(**_source.dict()), id=source_id, db=db)

        # Update Source Videos from Fetched Videos
        # db_source = await self.get(id=source_id)
        fetched_videos = await get_source_videos_from_source_info_dict(
            source_info_dict=source_info_dict
        )

        added_videos = await add_new_source_videos_from_fetched_videos(
            fetched_videos=fetched_videos, db_source=db_source, db=db
        )

        # NOTE: Enable if db grows too large. Otherwise best not to delete any videos
        # from database as podcast app will still reference the video's feed_media_url
        # deleted_videos = await delete_orphaned_source_videos(
        #     fetched_videos=fetched_videos, db_source=db_source
        # )
        deleted_videos: list[Video] = []

        refreshed_videos = await refresh_videos(videos=db_source.videos, db=db)

        # Build RSS File
        await build_rss_file(source=db_source)

        logger.success(
            f"Completed fetching Source(id='{db_source.id}'). "
            f"[{len(added_videos)}/{len(deleted_videos)}/{len(refreshed_videos)}] "
            f"Added {len(added_videos)} new videos. "
            f"Deleted {len(deleted_videos)} orphaned videos. "
            f"Refreshed {len(refreshed_videos)} videos."
        )

        return await self.get(id=source_id, db=db)

    async def fetch_all_sources(self, db: Session) -> list[Source]:
        """
        Fetch all sources.

        Args:
            db (Session): The database session.

        Returns:
            List[Source]: List of fetched sources
        """
        logger.warning("Fetching ALL Sources...")
        sources = await self.get_all(db=db) or []
        fetched = []
        for _source in sources:
            fetched.append(await self.fetch_source(source_id=_source.id, db=db))

        return fetched

    async def fetch_source_videos(self, source_id: str, db: Session) -> Source:
        """Fetch new data from yt-dlp for each video in the source.

        Args:
            source_id: The ID of the source to fetch videos for.
            db (Session): The database session.

        Returns:
            The source with the updated videos.
        """
        # Get the source from the database
        _source = await self.get(id=source_id, db=db)

        # Fetch new data for each video in the source
        for video in _source.videos:
            await crud.video.fetch_video(video_id=video.id, db=db)

        # Return the updated source
        return await self.get(id=source_id, db=db)


source = SourceCRUD(Source)
