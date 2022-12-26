from sqlmodel import Session
from sqlmodel_basecrud import BaseRepository  # type: ignore

from youtube_rss.db.database import engine
from youtube_rss.models.source import Source
from youtube_rss.models.video import Video

with Session(engine) as session:
    video_crud = BaseRepository(db=session, model=Video)
    source_crud = BaseRepository(db=session, model=Source)
