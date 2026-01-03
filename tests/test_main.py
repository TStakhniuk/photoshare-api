import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """
    Verifies that the application starts correctly and the root endpoint returns a 200 OK status with the welcome message.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PhotoShare API"}