import pytest
from httpx import AsyncClient
from src.main import app  # імпортуйте ваш додаток FastAPI


@pytest.mark.asyncio
async def test_get_photos(client: AsyncClient):
    """Тестуємо отримання списку фото"""
    response = await client.get("/photos/")
    assert response.status_code == 200
    assert "items" in response.json()

@pytest.mark.asyncio
async def test_get_photo_not_found(client: AsyncClient):
    """Тестуємо випадок, коли фото не існує"""
    response = await client.get("/api/photos/999999")
    assert response.status_code == 404