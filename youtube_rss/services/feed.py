from typing import Any

import datetime
from pathlib import Path

from feedgen.feed import FeedGenerator
from loguru import logger

from youtube_rss.config import USE_CACHE
from youtube_rss.constants import BASE_DOMAIN
from youtube_rss.db.crud import source_crud
from youtube_rss.models.source import Source
from youtube_rss.paths import FEEDS_PATH
from youtube_rss.services.source import get_source, get_source_info_dict


# RSS File
def get_rss_file_path(feed_id: str) -> Path:
    """
    Returns the file path for a 'feed_id' rss file.
    """
    return FEEDS_PATH / f"{feed_id}.rss"


def get_rss_file(feed_id: str) -> Path:
    """
    Returns a validated rss file.
    """
    rss_file = get_rss_file_path(feed_id=feed_id)

    # Validate RSS File exists
    if not rss_file.exists():
        err_msg = f"RSS file ({feed_id}.rss) does not exist for ({feed_id=})"
        logger.warning(err_msg)
        raise FileNotFoundError(err_msg)
    return rss_file


def delete_rss_file(feed_id: str):
    rss_file = get_rss_file_path(feed_id=feed_id)
    rss_file.unlink()


def build_rss_file(feed_id: str) -> Path:
    """
    Builds a .rss file for source_id, saves it to disk.
    """
    feed = YoutubeFeed(feed_id=feed_id)
    feed.generate()
    return feed.save()


def build_all_rss_files() -> None:
    """
    Build .rss files for all sources, save to disk."""
    sources = source_crud.get_all()
    for source in sources:
        build_rss_file(feed_id=source.source_id)


class YoutubeFeed:
    def __init__(self, feed_id: str) -> None:
        """
        Generate a RSS Feed from Youtube Link
        """
        self.feed_id = feed_id
        self.feed: FeedGenerator = FeedGenerator()
        self.feed.load_extension("podcast")

    def generate_rss_header(
        self, feed: FeedGenerator, source: Source, source_info_dict: dict[str, Any]
    ) -> FeedGenerator:
        """
        Generates header for a FeedGenerator feed.
        """
        feed.title(source.name)
        feed.link(href=f"{BASE_DOMAIN}/feed/{source.source_id}", rel="self")

        feed.id(source_info_dict["uploader_id"])
        feed.author({"name": source_info_dict["uploader"]})
        feed.link(href=source_info_dict["uploader_url"], rel="alternate")
        feed.logo(source_info_dict["thumbnails"][2]["url"])
        feed.subtitle("Generated by YoutubeRSS")
        feed.description("Generated by YoutubeRSS")
        return feed

    def generate_rss_posts(
        self, feed: FeedGenerator, source_info_dict: dict[str, Any]
    ) -> FeedGenerator:
        """
        Generates rss posts for a FeedGenerator feed.
        """
        # TODO: FIXME, not working with 'UCddAESxyImvJYe7LMlfdxCA'
        entries = source_info_dict.get("entries", [])
        for item in entries:
            if item.get("entries"):
                # Handle as List of Playlists
                item_entires = item.get("entries", [])
                for video in item_entires:
                    feed = self.generate_rss_post(feed=feed, video=video)
            else:
                # Handle as List of Videos
                feed = self.generate_rss_post(feed=feed, video=item)
        return feed

    def generate_rss_post(self, feed: FeedGenerator, video: dict[str, Any]) -> FeedGenerator:
        """
        Generates rss post for a FeedGenerator feed.
        """
        post = feed.add_entry()
        post.author({"name": video.get("uploader")})
        post.id(video["original_url"])
        post.title(video["title"])
        post.description(video["description"])
        post.enclosure(url=video["url"], length=str(video["filesize_approx"]), type="video/mp4")
        post.published(
            datetime.datetime.strptime(video["upload_date"], "%Y%m%d").replace(
                tzinfo=datetime.timezone.utc
            )
        )
        return feed

    def generate(self) -> None:
        """
        Generate a FeedGenerator Feed
        """
        source = get_source(source_id=self.feed_id)
        source_info_dict = get_source_info_dict(
            source_id=source.source_id,
            url=source.url,
            use_cache=USE_CACHE,
        )  # TODO: Currently ALWAYS using cache. Decide how to properly handle this

        self.feed = self.generate_rss_header(
            feed=self.feed, source=source, source_info_dict=source_info_dict
        )
        self.feed = self.generate_rss_posts(feed=self.feed, source_info_dict=source_info_dict)

    def save(self) -> Path:
        """
        Saves a generated feed to file. Returns file path
        """
        rss_file = get_rss_file_path(feed_id=self.feed_id)
        if not self.feed:
            self.generate()
        self.feed.rss_file(rss_file, encoding="UTF-8", pretty=True)
        return rss_file
