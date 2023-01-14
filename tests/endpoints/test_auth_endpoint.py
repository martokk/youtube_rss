import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlmodel import Session

from youtube_rss.api.v1.endpoints.auth import login, register
from youtube_rss.core.auth import AuthHandler
from youtube_rss.models.user import UserCreate, UserDB, UserLogin


async def test_client(db: Session, auth_handler: AuthHandler) -> None:
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )

    users = db.query(UserDB).all()
    assert len(users) == 0

    result = await register(user_create, db)
    assert isinstance(result, UserDB)

    assert result.username == "test_user"
    assert result.email == "test@example.com"

    # assert that the password is hashed
    assert result.password != "test_password"
    assert result.password.startswith("$2b")
    assert auth_handler.verify_password(
        plain_password="test_password", hashed_password=result.password
    )


async def test_register_username_taken(db: Session) -> None:
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )

    result = await register(user_create, db)
    assert isinstance(result, UserDB)

    with pytest.raises(HTTPException) as e:
        await register(user_create, db)
    assert e.value.status_code == status.HTTP_409_CONFLICT
    assert e.value.detail == "Username is taken."


async def test_register_email_taken(db: Session) -> None:
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    user_create_2 = UserCreate(
        username="test_user2", email="test@example.com", password="test_password2"
    )

    result = await register(user_create, db)
    assert isinstance(result, UserDB)

    with pytest.raises(HTTPException) as e:
        await register(user_create_2, db)
    assert e.value.status_code == status.HTTP_409_CONFLICT
    assert e.value.detail == "Email already registered."


async def test_login_success(db: Session, auth_handler: AuthHandler) -> None:
    # Create a test user
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    user_db = await register(user_create, db)
    user_login = UserLogin(username="test_user", password="test_password")

    # Try logging in the user
    result = await login(user_login, db)
    assert "access_token" in result
    assert "refresh_token" in result
    assert auth_handler.decode_access_token(result["access_token"]) == user_db.id
    assert auth_handler.decode_refresh_token(result["refresh_token"]) == user_db.id


async def test_login_wrong_password(db: Session) -> None:
    # Create a test user
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    await register(user_create, db)

    # Try logging in the user
    user_login = UserLogin(username="test_user", password="wrong_password")
    with pytest.raises(HTTPException) as e:
        await login(user_login, db)
    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.detail == "Invalid username and/or password."


async def test_login_wrong_username(db: Session) -> None:
    # Create a test user
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    await register(user_create, db)

    # Try logging in the user
    user_login = UserLogin(username="wrong_username", password="test_password")
    with pytest.raises(HTTPException) as e:
        await login(user_login, db)
    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.detail == "Invalid username and/or password."


async def test_protected_success(db: Session, client: TestClient) -> None:
    # Create a test user
    user_create = UserCreate(
        username="test_user", email="test@example.com", password="test_password"
    )
    user_db = await register(user_create, db)

    # login user
    user_login = UserLogin(username="test_user", password="test_password")
    tokens = await login(user_login, db)

    # Try accessing the protected endpoint
    access_token = tokens["access_token"]
    response = client.get("/protected", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    result = response.json()
    assert result["authenticated"] is True
    assert result["user_id"] == user_db.id


def test_protected_unauthenticated(client: TestClient) -> None:
    response = client.get("/protected")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_protected_invalid_token(client: TestClient):
    response = client.get("/protected", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Token"
