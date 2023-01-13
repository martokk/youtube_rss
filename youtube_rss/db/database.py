from sqlmodel import create_engine

from youtube_rss.config import DATABASE_ECHO
from youtube_rss.paths import DATABASE_FILE

database_url = f"sqlite:///{DATABASE_FILE}"

connect_args = {"check_same_thread": False}
engine = create_engine(database_url, echo=DATABASE_ECHO, connect_args=connect_args)
