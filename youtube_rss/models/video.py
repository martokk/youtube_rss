from typing import Optional

from sqlmodel import Field, SQLModel


class Video(SQLModel, table=True):
    video_id: str = Field(primary_key=True, nullable=False)
    title: str = Field()
    description: str = Field()
    url: str = Field()
    mp4_url: Optional[str] = Field(nullable=True)
