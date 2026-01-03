from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.users.models import User, Role
from src.users.enums import RoleEnum
from src.users.schemas import UserCreate
from src.auth.security import get_password_hash


async def count_users(db: AsyncSession) -> int:
    """
    Counts the total number of users in the database.

    :param db: The database session.
    :return: The count of users.
    """
    result = await db.execute(select(func.count(User.id)))
    return result.scalar()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """
    Creates a new user in the database.

    :param db: The database session.
    :param data: The data required to create a user (username, email, password, role).
    :return: The newly created User object.
    """
    hashed_password = get_password_hash(data.password)

    users_count = await count_users(db)

    if users_count == 0:
        role_name = RoleEnum.ADMIN.value
    else:
        role_name = RoleEnum.USER.value

    role = await get_role_by_name(db, role_name)

    new_user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
        role=role,
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


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    """
    Retrieves a role by its name.

    :param db: The database session.
    :param name: The name of the role.
    :return: The Role object if found, otherwise None.
    """
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Retrieves a user by their ID.

    :param db: The database session.
    :param user_id: The user ID to search for.
    :return: The User object if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, update_data: dict) -> User:
    """
    Updates user information in the database.

    :param db: The database session.
    :param user: The User object to update.
    :param update_data: Dictionary containing fields to update.
    :return: The updated User object.
    """
    for field, value in update_data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user


async def toggle_user_active_status(db: AsyncSession, user: User, is_active: bool) -> User:
    """
    Toggles the active status of a user account.

    :param db: The database session.
    :param user: The User object to update.
    :param is_active: The new active status (True for active, False for inactive).
    :return: The updated User object.
    """
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)
    return user