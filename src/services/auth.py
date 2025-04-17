from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiocache import cached

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.database.models import User, UserRole


class Hash:
    """
    Password hashing and verification helper.
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a hashed password.

        Parameters:
        - plain_password: str – the password to verify.
        - hashed_password: str – the hashed password for comparison.

        Returns:
        - bool: True if the password matches, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hash a plain-text password.

        Parameters:
        - password: str – the password to hash.

        Returns:
        - str: The hashed password.
        """
        return self.pwd_context.hash(password)

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def _build_token(data: dict, expires_delta: timedelta) -> str:
    """
    Build a JWT access token with an expiration and issue time.

    Parameters:
    - data: dict – the payload data.
    - expires_delta: timedelta – the token's lifetime.

    Returns:
    - str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Create an access token for authentication.

    Parameters:
    - data: dict – the payload to include in the token.
    - expires_delta: Optional[int] – custom expiration time in seconds (default from settings).

    Returns:
    - str: Encoded JWT access token.
    """
    delta = timedelta(seconds=expires_delta or settings.JWT_EXPIRATION_SECONDS)
    return _build_token(data, delta)


def cache_key_builder(func, args, kwargs) -> str:
    """
    Generate a cache key based on the username argument.

    Parameters:
    - func: Callable – the function being decorated.
    - args: tuple – positional arguments passed to the function.
    - kwargs: dict – keyword arguments passed to the function.

    Returns:
    - str: A cache key.
    """
    return f"username: {args[0]}"


@cached(ttl=300, key_builder=cache_key_builder)
async def get_user_from_db(username: str, db: AsyncSession) -> User:
    """
    Retrieve a user from the database using cache.

    Parameters:
    - username: str – the username to look up.
    - db: AsyncSession – the database session.

    Returns:
    - User: The user object.
    """
    print("NOT CACHED USER")
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract the current user from the JWT token and fetch from the database.

    Parameters:
    - token: str – JWT token from request header.
    - db: AsyncSession – the database session.

    Returns:
    - User: The current authenticated user.

    Raises:
    - HTTPException: If the token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print("[DEBUG] ORIGINAL get_current_user CALLED1")
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Validate that the current user is an admin.

    Parameters:
    - current_user: User – the current user from dependency injection.

    Returns:
    - User: The user if they are an admin.

    Raises:
    - HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user


def create_email_token(data: dict) -> str:
    """
    Create a token for email verification or recovery.

    Parameters:
    - data: dict – the payload to include.

    Returns:
    - str: Encoded JWT token valid for 7 days.
    """
    delta = timedelta(days=7)
    return _build_token(data, delta)


async def get_email_from_token(token: str) -> str:
    """
    Extract email from a JWT token.

    Parameters:
    - token: str – the JWT token.

    Returns:
    - str: The extracted email (subject).

    Raises:
    - HTTPException: If token is invalid or email is missing.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            raise ValueError("Missing subject in token")
        return email
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


async def get_password_from_token(token: str) -> str:
    """
    Extract password from a password reset token.

    Parameters:
    - token: str – the JWT token.

    Returns:
    - str: The extracted password.

    Raises:
    - HTTPException: If token is invalid or malformed.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        password = payload["password"]
        return password
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        )