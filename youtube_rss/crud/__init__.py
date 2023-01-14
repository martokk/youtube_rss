# from sqlmodel import Session

# from youtube_rss.core.database import engine

# from .source import SourceCRUD
# from .user import UserCRUD
# from .video import VideoCRUD

# with Session(engine) as session:
#     video_crud = VideoCRUD(session=session)
#     source_crud = SourceCRUD(session=session)
#     user_crud = UserCRUD(session=session)

from .exceptions import (
    DeleteError,
    InvalidRecordError,
    RecordAlreadyExistsError,
    RecordNotFoundError,
)
from .source import source
from .user import user
from .video import video

__all__ = [
    "source",
    "user",
    "video",
    "DeleteError",
    "InvalidRecordError",
    "RecordAlreadyExistsError",
    "RecordNotFoundError",
]
