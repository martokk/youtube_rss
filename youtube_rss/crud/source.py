from sqlmodel import Session

from youtube_rss.core.debug_helpers import timeit
from youtube_rss.crud.exceptions import RecordAlreadyExistsError
from youtube_rss.crud.video import refresh_videos, video_crud
from youtube_rss.db.database import engine
from youtube_rss.models.source import Source, SourceCreate, SourceRead
from youtube_rss.services.feed import build_rss_file
from youtube_rss.services.source import (
    generate_source_id_from_url,
    get_source_from_source_info_dict,
    get_source_info_dict,
)

from .base import BaseCRUD


class SourceCRUD(BaseCRUD[Source, SourceCreate, SourceRead]):
    def __init__(self, session: Session) -> None:
        super().__init__(model=Source, session=session)

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
            use_cache=False,
        )
        source = await get_source_from_source_info_dict(source_info_dict=source_info_dict)

        # Save the source to the database
        db_source = await self.create(source)

        # Fetch video information from yt-dlp for new videos
        await refresh_videos(videos=db_source.videos)

        return db_source

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
            use_cache=False,
        )
        fetched_source = await get_source_from_source_info_dict(source_info_dict=source_info_dict)

        # Save the source to the database
        db_source = await self.update(SourceCreate(**fetched_source.dict()), id=fetched_source.id)

        # Delete orphaned Videos no longer in the Source
        await self.delete_orphaned_source_videos(fetched_source=fetched_source, db_source=db_source)

        # Fetch video information from yt-dlp for new videos
        await refresh_videos(videos=db_source.videos)

        # Build RSS File
        await build_rss_file(source=db_source)

        return await self.get(id=fetched_source.id)

    async def delete_orphaned_source_videos(
        self, fetched_source: Source, db_source: Source
    ) -> None:
        """Delete videos that are no longer present in `fetched_source`.

        Args:
        - fetched_source: The source object to compare the videos against.
        - db_source: The source object in the database to delete videos from.
        """
        fetched_video_ids = [video.id for video in fetched_source.videos]

        # Iterate through the videos in the source in the database
        for db_video in db_source.videos:
            if db_video.id not in fetched_video_ids:
                await video_crud.delete(id=db_video.id)

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


@timeit
async def refresh_all_sources() -> list[Source]:
    """
    Fetches new data for all sources from yt-dlp.

    Returns:
        The refreshed list of sources.
    """
    sources = await source_crud.get_all() or []
    return await refresh_sources(sources=sources)


@timeit
async def refresh_sources(sources: list[Source]) -> list[Source]:
    """
    Fetches new data for a list of sources from yt-dlp.

    Args:
        sources: The list of sources to refresh.

    Returns:
        The refreshed list of sources.
    """
    return [await source_crud.fetch_source(source_id=source.id) for source in sources]
