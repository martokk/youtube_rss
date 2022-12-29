from typing import Any, Optional

from pydantic import root_validator
from sqlmodel import Field, SQLModel

from youtube_rss.constants import BASE_URL


class SourceBase(SQLModel):
    url: str = Field()


class Source(SourceBase, table=True):
    source_id: str = Field(primary_key=True, nullable=False)
    name: str = Field()
    feed_url: Optional[str] = Field(nullable=True)

    @root_validator
    def create_feed_url(  # pylint: disable=no-self-argument
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        source_id = values.get("source_id")
        values["feed_url"] = f"{BASE_URL}/feed/{source_id}"
        return values


class SourceCreate(SourceBase):
    pass
