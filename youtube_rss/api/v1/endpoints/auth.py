from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from youtube_rss.api.v1.deps import get_active_user_id
from youtube_rss.core.auth import AuthHandler
from youtube_rss.crud.exceptions import RecordNotFoundError
from youtube_rss.crud.user import user_crud
from youtube_rss.models.user import UserCreate, UserDB, UserLogin, UserRead

router = APIRouter()

auth_handler = AuthHandler()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    summary="Create new user",
)
async def register(user_create: UserCreate) -> UserDB:
    """
    Register a new user.

    Args:
        user_create (UserCreate): the user information for registration

    Returns:
        UserDB: an UserDB object

    Raises:
        HTTPException: if the username is already taken.
    """

    # Check if username/email is already taken.
    users = await user_crud.get_all() or []
    if any(user.username == user_create.username for user in users):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is taken.")
    if any(user.email == user_create.email for user in users):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )

    # Hash Password
    hashed_password = auth_handler.get_password_hash(password=user_create.password)
    user_create.password = hashed_password

    # Save to Database
    user = UserDB(**user_create.dict())
    return await user_crud.create(user)


@router.post("/login", summary="Create access and refresh tokens for user")
async def login(user_login: UserLogin) -> dict[str, str]:
    """
    Log in an existing user.

    Args:
        user_login (UserLogin): the user information for login

    Returns:
        dict: A dictionary containing the authentication token

    Raises:
        HTTPException: if the username and/or password is invalid
    """
    invalid_username_password_text = "Invalid username and/or password."
    try:
        user = await user_crud.get(username=user_login.username)
    except RecordNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=invalid_username_password_text
        ) from e

    # Handle wrong password.
    if not auth_handler.verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=invalid_username_password_text
        )

    return {
        "access_token": auth_handler.encode_access_token(user_id=user.id),
        "refresh_token": auth_handler.encode_refresh_token(user_id=user.id),
    }


@router.get("/protected")
def protected(user_id: str = Depends(get_active_user_id())) -> dict[str, bool | Any]:
    """
    Protected endpoint, can be accessed only by authenticated users

    Args:
        user_id (str): The authenticated user_id.

    Returns:
        dict: A dictionary with authenticated user name
    """
    return {"authenticated": True, "user_id": user_id}
