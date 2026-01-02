from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.auth.dependencies import oauth2_scheme, get_current_user
from src.database.redis import get_redis
from src.auth.token_blacklist import add_token_to_blacklist
import redis.asyncio as redis
from src.users.models import User
from src.users.schemas import UserCreate, UserResponse
from src.auth.schemas import Token, TokenRefresh
from src.users.repository import create_user, get_user_by_email, get_user_by_username
from src.auth.utils import create_access_token, create_refresh_token, decode_token
from src.auth.security import verify_password

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user in the system.

    :param user_data: The data required to create a new user (username, email, password).
    :param db: The database session dependency.
    :return: The newly created user's information.
    """
    existing_user_email = await get_user_by_email(db, user_data.email)
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    existing_user_username = await get_user_by_username(db, user_data.username)
    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists"
        )

    new_user = await create_user(db, user_data)

    return new_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user and issues access and refresh tokens.
    Inactive users cannot log in.

    :param form_data: The login credentials (username as email and password).
    :param db: The database session dependency.
    :return: A dictionary containing the access token, refresh token, and token type.
    """
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh_tokens(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """
    Generates a new access token using a valid refresh token.

    :param data: The refresh token required to generate a new pair of tokens.
    :param db: The database session dependency.
    :return: A new pair of access and refresh tokens.
    """
    token_data = decode_token(data.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_email(db, token_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis)
):
    """
    Logs out the current user by invalidating their access token.

    :param token: The access token to invalidate.
    :param current_user: The currently authenticated user (ensures the token is valid before logging out).
    :param redis_client: The Redis client dependency.
    """
    await add_token_to_blacklist(token, redis_client)