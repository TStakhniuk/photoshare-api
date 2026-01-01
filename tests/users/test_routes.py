import pytest
from httpx import AsyncClient
from fastapi import status

from src.users.models import User
from src.auth.utils import create_access_token
from src.users.repository import create_user
from src.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_get_my_profile(client: AsyncClient, test_user: User):
    """Test getting own profile with authentication."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/users/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert "created_at" in data
    assert data["photos_count"] == 0


@pytest.mark.asyncio
async def test_get_my_profile_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot access /me endpoint."""
    response = await client.get("/users/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_user_profile_by_username(client: AsyncClient, test_user: User):
    """Test getting public user profile by username."""
    response = await client.get(f"/users/{test_user.username}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["username"] == test_user.username
    assert "created_at" in data
    assert data["photos_count"] == 0
    # Email should not be in public profile
    assert "email" not in data


@pytest.mark.asyncio
async def test_get_user_profile_not_found(client: AsyncClient):
    """Test getting profile for non-existent user returns 404."""
    response = await client.get("/users/nonexistent")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_my_profile_username(client: AsyncClient, test_user: User, session, faker):
    """Test updating own profile username."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    new_username = faker.user_name()
    update_data = {"username": new_username}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == new_username
    assert data["email"] == test_user.email  # Email should remain unchanged
    assert data["id"] == test_user.id


@pytest.mark.asyncio
async def test_update_my_profile_email(client: AsyncClient, test_user: User, faker):
    """Test updating own profile email."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    new_email = faker.email()
    update_data = {"email": new_email}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == new_email
    assert data["username"] == test_user.username  # Username should remain unchanged


@pytest.mark.asyncio
async def test_update_my_profile_both_fields(client: AsyncClient, test_user: User, faker):
    """Test updating both username and email."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    new_username = faker.user_name()
    new_email = faker.email()
    update_data = {
        "username": new_username,
        "email": new_email
    }
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == new_username
    assert data["email"] == new_email


@pytest.mark.asyncio
async def test_update_my_profile_no_changes(client: AsyncClient, test_user: User):
    """Test updating profile with no changes returns current data."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_update_my_profile_username_conflict(client: AsyncClient, test_user: User, session, faker, user_data):
    """Test that updating to existing username returns 409."""
    # Create another user using faker
    existing_username = faker.user_name()
    other_user_data = UserCreate(
        username=existing_username,
        email=faker.email(),
        password=user_data["password"]
    )
    await create_user(session, other_user_data)
    
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {"username": existing_username}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "username already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_my_profile_email_conflict(client: AsyncClient, test_user: User, session, faker, user_data):
    """Test that updating to existing email returns 409."""
    # Create another user using faker
    existing_email = faker.email()
    other_user_data = UserCreate(
        username=faker.user_name(),
        email=existing_email,
        password=user_data["password"]
    )
    await create_user(session, other_user_data)
    
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {"email": existing_email}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "email already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_my_profile_same_username_allowed(client: AsyncClient, test_user: User):
    """Test that updating to the same username is allowed."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {"username": test_user.username}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username


@pytest.mark.asyncio
async def test_update_my_profile_same_email_allowed(client: AsyncClient, test_user: User):
    """Test that updating to the same email is allowed."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {"email": test_user.email}
    response = await client.put("/users/me", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_update_my_profile_unauthorized(client: AsyncClient):
    """Test that unauthenticated users cannot update profile."""
    update_data = {"username": "newusername"}
    response = await client.put("/users/me", json=update_data)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



