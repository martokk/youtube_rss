from typing import TYPE_CHECKING, Any

import datetime

from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from youtube_rss.handlers import get_handler_from_url
from youtube_rss.services.uuid import generate_uuid_from_url

if TYPE_CHECKING:
    from youtube_rss.models.source import Source


class VideoBase(SQLModel):
    id: str = Field(default=None, primary_key=True, nullable=False)
    source_id: str = Field(default=None, foreign_key="source.id", nullable=False)
    handler: str = Field(default=None, nullable=False)
    uploader: str | None = Field(default=None)
    uploader_id: str | None = Field(default=None)
    title: str | None = Field(default=None)
    description: str | None = Field(default=None)
    duration: int | None = Field(default=None)
    thumbnail: str | None = Field(default=None)
    url: str = Field(default=None)
    media_url: str | None = Field(default=None)
    feed_media_url: str | None = Field(default=None)
    media_filesize: int | None = Field(default=None)
    released_at: datetime.datetime | None = Field(default=None)
    added_at: datetime.datetime = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)


class Video(VideoBase, table=True):
    source: "Source" = Relationship(back_populates="videos")

    @root_validator(pre=True)
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        handler = get_handler_from_url(url=values["url"])
        sanitized_url = handler.sanitize_video_url(url=values["url"])
        video_id = generate_uuid_from_url(url=sanitized_url)
        feed_media_url = f"/media/{video_id}"
        return {
            **values,
            "handler": handler.name,
            "url": sanitized_url,
            "id": video_id,
            "feed_media_url": feed_media_url,
            "updated_at": datetime.datetime.now(tz=datetime.timezone.utc),
        }

    @root_validator
    def create_added_at(cls, values: dict[str, Any | None]) -> dict[str, Any]:
        if not values.get("added_at"):
            values["added_at"] = datetime.datetime.now(tz=datetime.timezone.utc)
        return values


class VideoCreate(VideoBase):
    @root_validator
    def create_updated_at(cls, values: dict[str, Any | None]) -> dict[str, Any]:
        values["updated_at"] = datetime.datetime.now(tz=datetime.timezone.utc)
        return values

    @root_validator
    def create_released_at(cls, values: dict[str, Any | None]) -> dict[str, Any]:
        values["released_at"] = values["released_at"]
        return values


class VideoUpdate(VideoCreate):
    pass


class VideoRead(VideoBase):
    source_id: str = Field(default=None, foreign_key="source.id")


async def generate_video_id_from_url(url: str) -> str:
    handler = get_handler_from_url(url=url)
    sanitized_video_url = handler.sanitize_video_url(url=url)
    return generate_uuid_from_url(url=sanitized_video_url)
