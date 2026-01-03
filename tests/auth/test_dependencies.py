import pytest
from fastapi import HTTPException, status
from src.auth.dependencies import RoleChecker
from src.users.enums import RoleEnum
from src.users.models import User, Role
from src.auth.dependencies import get_current_user
from src.auth.utils import create_access_token

class MockUser:
    def __init__(self, role_name):
        self.role = Role(name=role_name)

@pytest.mark.asyncio
async def test_role_checker_allowed():
    """
    Verifies that a user with the required role is granted access by the RoleChecker.
    """
    checker = RoleChecker([RoleEnum.ADMIN])
    user = MockUser(role_name="admin")

    result = await checker(user)
    assert result == user

@pytest.mark.asyncio
async def test_role_checker_forbidden():
    """
    Verifies that a user without the required role is denied access and receives a 403 Forbidden error.
    """
    checker = RoleChecker([RoleEnum.ADMIN])
    user = MockUser(role_name="user")

    with pytest.raises(HTTPException) as exc_info:
        await checker(user)

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "You do not have permission to perform this action"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(session, mock_redis):
    """
    Verifies that providing an invalid or malformed token raises a 401 Unauthorized error.
    """
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="invalid_token", db=session, redis_client=mock_redis)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_current_user_deleted_from_db(session, mock_redis):
    """
    Verifies that if a user has a valid token but has been deleted from the database, a 401 Unauthorized error is raised.
    """
    token = create_access_token(data={"sub": "deleted@example.com"})

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=token, db=session, redis_client=mock_redis)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Could not validate credentials"