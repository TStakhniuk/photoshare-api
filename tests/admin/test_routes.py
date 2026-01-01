import pytest
from httpx import AsyncClient
from fastapi import status

from src.users.models import User
from src.users.enums import RoleEnum
from src.auth.utils import create_access_token


@pytest.mark.asyncio
async def test_unban_user_by_username(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test unbanning a user by username as admin."""
    # First ban the user
    test_user.is_active = False
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Unban user
    response = await client.patch(
        f"/users/{test_user.username}/unban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is True
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role.name


@pytest.mark.asyncio
async def test_ban_user_by_username(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test banning a user by username as admin."""
    # Ensure user is active
    test_user.is_active = True
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Ban user
    response = await client.patch(
        f"/users/{test_user.username}/ban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is False
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email




@pytest.mark.asyncio
async def test_unban_user_not_found_by_username(client: AsyncClient, test_admin_user: User):
    """Test unbanning non-existent user by username returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.patch(
        "/users/nonexistent/unban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_ban_user_not_found_by_username(client: AsyncClient, test_admin_user: User):
    """Test banning non-existent user by username returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.patch(
        "/users/nonexistent/ban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_cannot_change_own_status_by_username(client: AsyncClient, test_admin_user: User):
    """Test that admin cannot change their own account status by username."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to ban own account
    response = await client.patch(
        f"/users/{test_admin_user.username}/ban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot change your own account status" in response.json()["detail"].lower()
    
    # Try to unban own account (should also fail)
    response = await client.patch(
        f"/users/{test_admin_user.username}/unban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot change your own account status" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_admin_cannot_unban_user(client: AsyncClient, test_user: User, session, user_data, faker):
    """Test that non-admin user cannot unban other users."""
    # Create a regular user using faker
    from src.users.schemas import UserCreate
    from src.users.repository import create_user
    
    regular_user_data = UserCreate(
        username=faker.user_name(),
        email=faker.email(),
        password=user_data["password"]
    )
    regular_user = await create_user(session, regular_user_data)
    
    # Get regular user token
    regular_token = create_access_token(data={"sub": regular_user.email})
    headers = {"Authorization": f"Bearer {regular_token}"}
    
    # Try to unban user
    response = await client.patch(
        f"/users/{test_user.username}/unban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not enough permissions" in response.json()["detail"].lower() or "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_admin_cannot_ban_user(client: AsyncClient, test_user: User, session, faker, user_data):
    """Test that non-admin user cannot ban other users."""
    # Create a regular user using faker
    from src.users.schemas import UserCreate
    from src.users.repository import create_user
    
    regular_user_data = UserCreate(
        username=faker.user_name(),
        email=faker.email(),
        password=user_data["password"]
    )
    regular_user = await create_user(session, regular_user_data)
    
    # Get regular user token
    regular_token = create_access_token(data={"sub": regular_user.email})
    headers = {"Authorization": f"Bearer {regular_token}"}
    
    # Try to ban user
    response = await client.patch(
        f"/users/{test_user.username}/ban",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not enough permissions" in response.json()["detail"].lower() or "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized_access_to_admin_endpoints(client: AsyncClient, test_user: User):
    """Test that unauthorized requests to admin endpoints return 401."""
    # Try without token
    response = await client.patch(
        f"/users/{test_user.username}/ban"
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

