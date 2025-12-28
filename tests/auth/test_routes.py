import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_route(client: AsyncClient, user_data):
    """
    Verifies successful user registration with valid data.
    """
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]

@pytest.mark.asyncio
async def test_signup_conflict_email(client: AsyncClient, user_data):
    """
    Verifies that registering with an email that already exists returns a 409 Conflict error.
    """
    await client.post("/auth/signup", json=user_data)
    response = await client.post("/auth/signup", json=user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"

@pytest.mark.asyncio
async def test_signup_conflict_username(client: AsyncClient, user_data):
    """
    Verifies that registering with a username that already exists (even with a different email) returns a 409 Conflict error.
    """
    await client.post("/auth/signup", json=user_data)

    user_data_2 = user_data.copy()
    user_data_2["email"] = "unique_email@example.com"

    response = await client.post("/auth/signup", json=user_data_2)
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this username already exists"

@pytest.mark.asyncio
async def test_login_route(client: AsyncClient, user_data):
    """
    Verifies successful user login and token generation.
    """
    await client.post("/auth/signup", json=user_data)
    login_data = {"username": user_data["email"], "password": user_data["password"]}
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, user_data):
    """
    Verifies that logging in with an incorrect password returns a 401 Unauthorized error.
    """
    await client.post("/auth/signup", json=user_data)
    login_data = {"username": user_data["email"], "password": "wrongpassword"}
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_login_user_not_found(client: AsyncClient):
    """
    Verifies that logging in with an email that does not exist returns a 401 Unauthorized error.
    """
    login_data = {"username": "ghost@example.com", "password": "password123"}
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_refresh_token_route(client: AsyncClient, user_data):
    """
    Verifies successful access token refresh using a valid refresh token.
    """
    await client.post("/auth/signup", json=user_data)
    login_res = await client.post("/auth/login",
                                  data={"username": user_data["email"], "password": user_data["password"]})
    refresh_token = login_res.json()["refresh_token"]

    await asyncio.sleep(1)

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """
    Verifies that attempting to refresh with an invalid token returns a 401 Unauthorized error.
    """
    response = await client.post("/auth/refresh", json={"refresh_token": "invalid_token_string"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_refresh_user_not_found(client: AsyncClient, user_data, session):
    """
    Verifies that refreshing a token for a user who has been deleted from the database returns a 401 Unauthorized error.
    """
    from sqlalchemy import text

    await client.post("/auth/signup", json=user_data)
    login_res = await client.post("/auth/login",
                                  data={"username": user_data["email"], "password": user_data["password"]})
    refresh_token = login_res.json()["refresh_token"]

    await session.execute(text(f"DELETE FROM users WHERE email = '{user_data['email']}'"))
    await session.commit()

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_logout_route(client: AsyncClient, user_data):
    """
    Verifies successful logout and that the token is subsequently blacklisted.
    """
    await client.post("/auth/signup", json=user_data)
    login_res = await client.post("/auth/login",
                                  data={"username": user_data["email"], "password": user_data["password"]})
    access_token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = await client.post("/auth/logout", headers=headers)
    assert response.status_code == 204

    response_again = await client.post("/auth/logout", headers=headers)
    assert response_again.status_code == 401