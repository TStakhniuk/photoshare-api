import pytest
from src.users.repository import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    count_users
)
from src.users.schemas import UserCreate
from src.users.enums import RoleEnum

@pytest.mark.asyncio
async def test_create_first_user_is_admin(session, user_data):
    """
    Verifies that the very first user created in the database is automatically assigned the ADMIN role.
    """
    user_in = UserCreate(**user_data)
    user = await create_user(session, user_in)

    assert user.email == user_data["email"]
    assert user.role.name == RoleEnum.ADMIN.value
    assert user.id is not None

@pytest.mark.asyncio
async def test_create_second_user_is_user(session, user_data, faker):
    """
    Verifies that subsequent users (after the first one) are assigned the USER role by default.
    """
    admin_in = UserCreate(**user_data)
    await create_user(session, admin_in)

    second_user_data = {
        "username": faker.user_name(),
        "email": faker.email(),
        "password": "password123"
    }
    user_in = UserCreate(**second_user_data)
    user = await create_user(session, user_in)

    assert user.email == second_user_data["email"]
    assert user.role.name == RoleEnum.USER.value

@pytest.mark.asyncio
async def test_get_user_by_email(session, user_data):
    """
    Verifies that a user can be successfully retrieved by their email address.
    """
    user_in = UserCreate(**user_data)
    await create_user(session, user_in)

    user = await get_user_by_email(session, user_data["email"])
    assert user is not None
    assert user.email == user_data["email"]

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(session):
    """
    Verifies that searching for a non-existent email returns None.
    """
    user = await get_user_by_email(session, "wrong@example.com")
    assert user is None

@pytest.mark.asyncio
async def test_get_user_by_username(session, user_data):
    """
    Verifies that a user can be successfully retrieved by their username.
    """
    user_in = UserCreate(**user_data)
    await create_user(session, user_in)

    user = await get_user_by_username(session, user_data["username"])
    assert user is not None
    assert user.username == user_data["username"]

@pytest.mark.asyncio
async def test_count_users(session, user_data):
    """
    Verifies that the user count logic works correctly, incrementing as new users are added.
    """
    assert await count_users(session) == 0

    user_in = UserCreate(**user_data)
    await create_user(session, user_in)

    assert await count_users(session) == 1