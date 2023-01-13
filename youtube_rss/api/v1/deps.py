from typing import Callable

from youtube_rss.core.auth import AuthHandler


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
