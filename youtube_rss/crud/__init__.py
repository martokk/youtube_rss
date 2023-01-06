from sqlmodel import Session

from youtube_rss.db.database import engine

from .source import SourceCRUD
from .video import VideoCRUD

with Session(engine) as session:
    video_crud = VideoCRUD(session=session)
    source_crud = SourceCRUD(session=session)
