from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from youtube_rss.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    JWT_REFRESH_SECRET_KEY,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)


class AuthHandler:
    """
    A class to handle the authentication and authorization.
    """

    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        """
        Get password hash from a plain password.

        Args:
            password (str): Plain password to be hashed.

        Returns:
            str: Hashed password.
        """
        return self.pwd_context.hash(secret=password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password (str): Plain password.
            hashed_password (str): Hashed password.

        Returns:
            bool: True if plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(secret=plain_password, hash=hashed_password)

    def encode_access_token(self, user_id: str) -> str:
        """
        Encode user id in token

        Args:
            user_id (str): user id to be encoded

        Returns:
            token (str): encoded token
        """
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(payload=payload, key=JWT_SECRET_KEY, algorithm=ALGORITHM)

    def encode_refresh_token(self, user_id: str) -> str:
        """
        Encode user id in refresh token

        Args:
            user_id (str): user id to be encoded

        Returns:
            refresh token (str): encoded token
        """
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "sub": user_id,
        }
        return jwt.encode(payload=payload, key=JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    def decode_access_token(self, token: str) -> str:
        """
        Decode token to get user_id

        Args:
            token (str): encoded token

        Returns:
            str: user_id from token

        Raises:
            HTTPException: when token is expired or invalid.
        """
        try:
            payload = jwt.decode(jwt=token, key=JWT_SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired Token"
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            ) from e
        return payload["sub"]

    def decode_refresh_token(self, token: str) -> str:
        """
        Decode token to get user_id

        Args:
            token (str): encoded token

        Returns:
            str: user_id from token

        Raises:
            HTTPException: when token is expired or invalid.
        """
        try:
            payload = jwt.decode(jwt=token, key=JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired Token"
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
            ) from e
        return payload["sub"]

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)) -> str:
        """
        Auth wrapper function that authenticate and return username

        Args:
            auth (HTTPAuthorizationCredentials): Authorization credentials to be verified

        Returns:
            str: username from token

        """
        return self.decode_access_token(token=auth.credentials)
