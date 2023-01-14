import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from youtube_rss import crud
from youtube_rss.core.app import app
from youtube_rss.core.auth import AuthHandler
from youtube_rss.models.source import SourceCreate
from youtube_rss.models.user import UserCreate
from youtube_rss.models.video import VideoCreate


@pytest.fixture(name="db")
def fixture_db() -> Session:
    test_db_uri = "sqlite:///:memory:"  # using an in-memory SQLite3 database
    test_engine = create_engine(test_db_uri)
    SQLModel.metadata.create_all(bind=test_engine)
    with Session(bind=test_engine) as session:
        return session


@pytest.fixture(name="auth_handler")
def fixture_auth_handler() -> AuthHandler:
    return AuthHandler()


@pytest.fixture(name="client")
def fixture_client() -> TestClient:
    return TestClient(app=app)


@pytest.fixture(name="db_with_user")
async def fixture_db_with_user(db: Session) -> Session:
    """
    Fixture that creates an example user in the test database.
    """
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    await crud.user.create(in_obj=user_create, db=db)
    return db


@pytest.fixture(name="db_with_source")
async def fixture_db_with_source(db_with_user: Session) -> Session:
    """
    Fixture that creates an example source in the test database.
    """
    source_create = SourceCreate(
        url="https://rumble.com/c/Styxhexenhammer666",
        name="Styxhexenhammer666",
        logo="https://sp.rmbl.ws/z8/t/j/s/b/tjsba.baa.1-Styxhexenhammer666-qyv16v.png",
        ordered_by="release",
        feed_url="/feed/7hyhcvzT",
        handler="RumbleHandler",
        updated_at=datetime.datetime(2023, 1, 14, 4, 5, 48, 123954),
        id="7hyhcvzT",
        author="Styxhexenhammer666",
        description="Styxhexenhammer666's Rumble Channel",
        extractor="CustomRumbleChannel",
        added_at=datetime.datetime.now(tz=datetime.timezone.utc),
        created_by="ZbFPeSXW",
    )
    await crud.source.create(in_obj=source_create, db=db_with_user)
    return db_with_user


@pytest.fixture(name="db_with_source_videos")
async def fixture_db_with_source_videos(db_with_source: Session) -> Session:
    """
    Fixture that creates example videos for the example source in the test database.
    """
    videos = []
    for i in range(3):
        video_create = VideoCreate(
            source_id="7hyhcvzT",
            handler="RumbleHandler",
            uploader=None,
            uploader_id=None,
            title=f"Example Video {i}",
            description=f"This is example video {i}.",
            duration=417,
            thumbnail="https://sp.rmbl.ws/s8d/R/0_FRh.oq1b.jpg",
            url=f"https://rumble.com/{i}{i}{i}{i}/test.html",
            media_url=None,
            feed_media_url="/media/CDYM2JpT",
            media_filesize=None,
            released_at=datetime.datetime(2023, 1, 10, 8, 17, 1),
            added_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        video = await crud.video.create(in_obj=video_create, db=db_with_source)
        videos.append(video)
    return db_with_source
