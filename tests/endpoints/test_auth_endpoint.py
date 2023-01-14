# import json

# import pytest
# from httpx import AsyncClient

# from youtube_rss.api.v1.endpoints.auth import router
# from youtube_rss.core.app import app
# from youtube_rss.crud.user import user_crud
# from youtube_rss.models.user import UserCreate, UserDB, UserLogin


# @pytest.fixture
# def async_client() -> AsyncClient:
#     client = AsyncClient(app=app, base_url="http://test")


# @pytest.mark.anyio
# async def test_register(async_client: AsyncClient) -> None:
#     user_create = UserCreate(username="testuser", email="testuser@example.com", password="password")

#     # Test successful registration
#     async with async_client as client:
#         await user_crud.delete(username="testuser")
#         response = await client.post("/register", json=user_create.dict())
#     assert response.status_code == 201
#     assert response.json()["username"] == "testuser"

#     # # Test registration with taken username
#     # response = client.post("/register", json=user_create.dict())
#     # assert response.status_code == 409
#     # assert response.json()["detail"] == "Username is taken."

#     # # Test registration with taken email
#     # user_create.username = "testuser2"
#     # response = client.post("/register", json=user_create.dict())
#     # assert response.status_code == 409
#     # assert response.json()["detail"] == "Email already registered."

#     # Clean up
#     await user_crud.delete(username="testuser")
#     await user_crud.delete(username="testuser2")


# # @pytest.mark.anyio
# # async def test_login(client):
# #     user_create = UserCreate(username="testuser", email="testuser@example.com", password="password")
# #     user = UserDB(**user_create.dict())
# #     await user_crud.create(user)

# #     # Test successful login
# #     user_login = UserLogin(username="testuser", password="password")
# #     response = client.post("/login", json=user_login.dict())
# #     assert response.status_code == 200
# #     assert "access_token" in response.json()
# #     assert "refresh_token" in response.json()

# #     # Test login with invalid username
# #     user_login.username = "invalidusername"
# #     response = client.post("/login", json=user_login.dict())
# #     assert response.status_code == 401
# #     assert response.json()["detail"] == "Invalid username and/or password."

# #     # Test login with invalid password
# #     user_login.username = "testuser"
# #     user_login.password = "wrongpassword"
# #     response = client.post("/login", json=user_login.dict())
# #     assert response.status_code == 401
# #     assert response.json()["detail"] == "Invalid username and/or password."

# #     # Clean up
# #     await user_crud.delete(username="testuser")
