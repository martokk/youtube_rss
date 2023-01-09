from typing import TYPE_CHECKING, Any

import datetime
from enum import Enum

from dateutil import tz
from pydantic import root_validator
from sqlmodel import Field, Relationship, SQLModel

from youtube_rss.config import BASE_URL
from youtube_rss.handlers import get_handler_from_url
from youtube_rss.services.uuid import generate_uuid_from_url

if TYPE_CHECKING:
    from youtube_rss.models.video import Video


class SourceOrderBy(Enum):
    RELEASE = "release"
    ADDED = "added"


class SourceBase(SQLModel):
    id: str = Field(default=None, primary_key=True, index=True)
    url: str = Field(default=None)
    name: str = Field(default=None)
    author: str = Field(default=None)
    logo: str = Field(default=None)
    description: str = Field(default=None)
    ordered_by: str = Field(default=None)
    feed_url: str = Field(default=None)
    extractor: str = Field(default=None)
    handler: str = Field(default=None)
    added_at: datetime.datetime = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)


class Source(SourceBase, table=True):
    videos: list["Video"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={
            "cascade": "all, delete",  # Instruct the ORM how to track changes to local objects
        },
    )

    @root_validator(pre=True)
    def set_pre_validation_defaults(cls, values: dict[str, Any]) -> dict[str, Any]:
        handler = get_handler_from_url(url=values["url"])
        sanitized_url = handler.sanitize_source_url(url=values["url"])
        source_id = generate_uuid_from_url(url=sanitized_url)
        feed_url = f"{BASE_URL}/feed/{source_id}"
        return {
            **values,
            "handler": handler.name,
            "url": sanitized_url,
            "id": source_id,
            "feed_url": feed_url,
            "ordered_by": SourceOrderBy.RELEASE.value,
            "added_at": values.get("added_at", datetime.datetime.now(tz=tz.tzutc())),
            "updated_at": datetime.datetime.now(tz=tz.tzutc()),
        }


class SourceCreate(SourceBase):
    @root_validator
    def create_updated_at(cls, values: dict[str, Any | None]) -> dict[str, Any]:
        values["updated_at"] = datetime.datetime.now(tz=tz.tzutc())
        return values


class SourceRead(SourceBase):
    pass


async def generate_source_id_from_url(url: str) -> str:
    handler = get_handler_from_url(url=url)
    sanitized_source_url = handler.sanitize_source_url(url=url)
    return generate_uuid_from_url(url=sanitized_source_url)
