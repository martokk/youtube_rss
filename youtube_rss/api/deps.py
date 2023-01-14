from collections.abc import Callable, Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from youtube_rss.core.auth import AuthHandler
from youtube_rss.core.database import engine


def get_active_user_id() -> Callable[..., str]:
    """
    Retrieves the authentication function for handling user authentication.
    This function, when called, will verify the provided authentication credentials
    and return the associated username if the credentials are valid.

    Returns:
        function: The authentication function that can be used to authenticate users.
    """
    return AuthHandler().auth_wrapper


def authenticated_user() -> Callable[..., str]:
    """
    Retrieves the authentication function for handling user authentication.
    This function, when called, will verify the provided authentication credentials
    and return the associated username if the credentials are valid.

    Returns:
        function: The authentication function that can be used to authenticate users.
    """
    return get_active_user_id()


def get_db() -> Generator[Session, None, None]:
    _session = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    session = _session()
    try:
        yield session
    finally:
        session.close()
