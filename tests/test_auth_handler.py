import jwt
import pytest

from youtube_rss.config import ALGORITHM, JWT_REFRESH_SECRET_KEY, JWT_SECRET_KEY
from youtube_rss.core.auth import AuthHandler


@pytest.fixture
def auth_handler() -> AuthHandler:
    return AuthHandler()


def test_get_password_hash(auth_handler: AuthHandler) -> None:
    plain_password = "password"
    hashed_password = auth_handler.get_password_hash(plain_password)
    assert auth_handler.pwd_context.verify(plain_password, hashed_password)


def test_verify_password(auth_handler: AuthHandler) -> None:
    plain_password = "password"
    hashed_password = auth_handler.get_password_hash(plain_password)
    assert auth_handler.verify_password(plain_password, hashed_password)


def test_encode_access_token(auth_handler: AuthHandler) -> None:
    user_id = "user1"
    token = auth_handler.encode_access_token(user_id)
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user_id


def test_encode_refresh_token(auth_handler: AuthHandler) -> None:
    user_id = "user1"
    token = auth_handler.encode_refresh_token(user_id)
    payload = jwt.decode(token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user_id


def test_decode_access_token(auth_handler: AuthHandler) -> None:
    user_id = "user1"
    token = auth_handler.encode_access_token(user_id)
    assert auth_handler.decode_access_token(token) == user_id


def test_decode_refresh_token(auth_handler: AuthHandler) -> None:
    user_id = "user1"
    token = auth_handler.encode_refresh_token(user_id)
    assert auth_handler.decode_refresh_token(token) == user_id
