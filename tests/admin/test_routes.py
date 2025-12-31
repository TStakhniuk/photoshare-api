import pytest
from httpx import AsyncClient
from fastapi import status

from src.users.models import User, UserRole
from src.auth.utils import create_access_token


@pytest.mark.asyncio
async def test_activate_user_by_id(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test activating a user by ID as admin."""
    # First deactivate the user
    test_user.is_active = False
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Activate user
    response = await client.put(
        f"/admin/users/{test_user.id}/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is True
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["role"] == UserRole.USER.value


@pytest.mark.asyncio
async def test_deactivate_user_by_id(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test deactivating a user by ID as admin."""
    # Ensure user is active
    test_user.is_active = True
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Deactivate user
    response = await client.put(
        f"/admin/users/{test_user.id}/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is False
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_activate_user_by_username(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test activating a user by username as admin."""
    # First deactivate the user
    test_user.is_active = False
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Activate user
    response = await client.put(
        f"/admin/users/{test_user.username}/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is True
    assert data["username"] == test_user.username


@pytest.mark.asyncio
async def test_deactivate_user_by_username(client: AsyncClient, test_user: User, test_admin_user: User, session):
    """Test deactivating a user by username as admin."""
    # Ensure user is active
    test_user.is_active = True
    await session.commit()
    await session.refresh(test_user)
    
    # Get admin token
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Deactivate user
    response = await client.put(
        f"/admin/users/{test_user.username}/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["is_active"] is False
    assert data["username"] == test_user.username


@pytest.mark.asyncio
async def test_activate_user_not_found_by_id(client: AsyncClient, test_admin_user: User):
    """Test activating non-existent user by ID returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.put(
        "/admin/users/99999/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deactivate_user_not_found_by_id(client: AsyncClient, test_admin_user: User):
    """Test deactivating non-existent user by ID returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.put(
        "/admin/users/99999/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_activate_user_not_found_by_username(client: AsyncClient, test_admin_user: User):
    """Test activating non-existent user by username returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.put(
        "/admin/users/nonexistent/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deactivate_user_not_found_by_username(client: AsyncClient, test_admin_user: User):
    """Test deactivating non-existent user by username returns 404."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = await client.put(
        "/admin/users/nonexistent/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_cannot_change_own_status_by_id(client: AsyncClient, test_admin_user: User):
    """Test that admin cannot change their own account status by ID."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to deactivate own account
    response = await client.put(
        f"/admin/users/{test_admin_user.id}/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot change your own account status" in response.json()["detail"].lower()
    
    # Try to activate own account (should also fail)
    response = await client.put(
        f"/admin/users/{test_admin_user.id}/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot change your own account status" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_admin_cannot_change_own_status_by_username(client: AsyncClient, test_admin_user: User):
    """Test that admin cannot change their own account status by username."""
    admin_token = create_access_token(data={"sub": test_admin_user.email})
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to deactivate own account
    response = await client.put(
        f"/admin/users/{test_admin_user.username}/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot change your own account status" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_admin_cannot_activate_user(client: AsyncClient, test_user: User, session):
    """Test that non-admin user cannot activate other users."""
    # Create a regular user
    from src.users.schemas import UserCreate
    from src.users.repository import create_user
    
    regular_user_data = UserCreate(
        username="regular",
        email="regular@example.com",
        password="password123"
    )
    regular_user = await create_user(session, regular_user_data)
    
    # Get regular user token
    regular_token = create_access_token(data={"sub": regular_user.email})
    headers = {"Authorization": f"Bearer {regular_token}"}
    
    # Try to activate user
    response = await client.put(
        f"/admin/users/{test_user.id}/activate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not enough permissions" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_non_admin_cannot_deactivate_user(client: AsyncClient, test_user: User, session):
    """Test that non-admin user cannot deactivate other users."""
    # Create a regular user
    from src.users.schemas import UserCreate
    from src.users.repository import create_user
    
    regular_user_data = UserCreate(
        username="regular2",
        email="regular2@example.com",
        password="password123"
    )
    regular_user = await create_user(session, regular_user_data)
    
    # Get regular user token
    regular_token = create_access_token(data={"sub": regular_user.email})
    headers = {"Authorization": f"Bearer {regular_token}"}
    
    # Try to deactivate user
    response = await client.put(
        f"/admin/users/{test_user.id}/deactivate",
        headers=headers
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not enough permissions" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_unauthorized_access_to_admin_endpoints(client: AsyncClient, test_user: User):
    """Test that unauthorized requests to admin endpoints return 401."""
    # Try without token
    response = await client.put(
        f"/admin/users/{test_user.id}/activate"
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

