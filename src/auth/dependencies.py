from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

from src.database.db import get_db
from src.database.redis import get_redis
from src.auth.utils import decode_token
from src.users.repository import get_user_by_email
from src.users.models import User
from src.users.enums import RoleEnum
from src.auth.token_blacklist import is_token_blacklisted


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
) -> User:
    """
    Retrieves the currently authenticated user based on the provided JWT token.

    :param token: The JWT access token extracted from the Authorization header.
    :param db: The database session dependency.
    :param redis_client: The Redis client for checking the token blacklist.
    :return: The User object corresponding to the token's subject (email).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None or token_data.email is None:
        raise credentials_exception

    # Check for blacklisting
    if await is_token_blacklisted(token, redis_client):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    user = await get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception

    return user


class RoleChecker:
    """
    Dependency callable class to check if the user has the required role.
    """
    def __init__(self, allowed_roles: list[RoleEnum]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        """
        Verifies the user's role against the allowed roles.

        :param user: The current authenticated user (injected by Depends).
        :return: The user object if access is granted.
        """
        if user.role.name not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user