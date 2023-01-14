from sqlmodel import SQLModel, create_engine

from youtube_rss import settings
from youtube_rss.core.logger import logger
from youtube_rss.paths import DATABASE_FILE

engine = create_engine(
    f"sqlite:///{DATABASE_FILE}",
    echo=settings.database_echo,
    connect_args={"check_same_thread": False},
)


async def create_db_and_tables() -> None:
    """Creates all SQLModel databases if not already created."""
    logger.debug("Initializing database...")
    SQLModel.metadata.create_all(engine)
