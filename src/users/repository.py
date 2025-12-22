from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.users.models import User
from src.users.schemas import UserCreate
from src.auth.security import get_password_hash


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """
    Creates a new user in the database.

    :param db: The database session.
    :param data: The data required to create a user (username, email, password).
    :return: The newly created User object.
    """
    hashed_password = get_password_hash(data.password)

    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Retrieves a user by their email address.

    :param db: The database session.
    :param email: The email address to search for.
    :return: The User object if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """
    Retrieves a user by their username.

    :param db: The database session.
    :param username: The username to search for.
    :return: The User object if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()