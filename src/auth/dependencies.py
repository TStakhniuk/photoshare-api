from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.auth.utils import decode_token
from src.users.repository import get_user_by_email
from src.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db),) -> User:
    """
    Retrieves the currently authenticated user based on the provided JWT token.

    :param token: The JWT access token extracted from the Authorization header.
    :param db: The database session dependency.
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

    user = await get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception

    return user
