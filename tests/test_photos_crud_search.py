import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from src.photos.schemas import PhotoCreate, PhotoUpdate, PhotoTransformRequest
from src.users.enums import RoleEnum

@pytest.mark.asyncio
async def test_upload_photo(client: AsyncClient, user_data, faker):
    """
    Тестує завантаження фото:
    - формат файлу правильний
    - додаються теги
    - опис фото
    """
    data = {
        "description": "Test photo",
        "tags": "nature,travel"
    }

    files = {
        "file": ("test.jpg", b"fake image content", "image/jpeg")
    }

    response = await client.post("/photos/", data=data, files=files)
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["description"] == "Test photo"
    assert "nature" in [t["name"] for t in res_json["tags"]]

@pytest.mark.asyncio
async def test_get_photos(client: AsyncClient):
    """
    Перевірка отримання списку фото з пагінацією
    """
    response = await client.get("/photos/?page=1&size=10")
    assert response.status_code == 200
    res_json = response.json()
    assert "items" in res_json
    assert "total" in res_json
    assert "page" in res_json
    assert "size" in res_json
    assert "pages" in res_json

@pytest.mark.asyncio
async def test_get_photo_by_id(client: AsyncClient):
    """
    Отримати конкретне фото по ID
    """
    # Створимо фото спочатку
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    data = {"description": "Single photo"}
    upload = await client.post("/photos/", data=data, files=files)
    photo_id = upload.json()["id"]

    response = await client.get(f"/photos/{photo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == photo_id

@pytest.mark.asyncio
async def test_update_photo(client: AsyncClient):
    """
    Оновлення опису фото
    """
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    data = {"description": "Original"}
    upload = await client.post("/photos/", data=data, files=files)
    photo_id = upload.json()["id"]

    update_data = {"description": "Updated"}
    response = await client.put(f"/photos/{photo_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"

@pytest.mark.asyncio
async def test_delete_photo(client: AsyncClient):
    """
    Видалення фото
    """
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    data = {"description": "To delete"}
    upload = await client.post("/photos/", data=data, files=files)
    photo_id = upload.json()["id"]

    response = await client.delete(f"/photos/{photo_id}")
    assert response.status_code == 204

    # Перевірка, що фото видалене
    get_resp = await client.get(f"/photos/{photo_id}")
    assert get_resp.status_code == 404

@pytest.mark.asyncio
async def test_search_photos(client: AsyncClient):
    """
    Пошук фото за описом та тегами
    """
    # Завантажуємо тестові фото
    files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
    await client.post("/photos/", data={"description": "Beach fun", "tags": "vacation,summer"}, files=files)
    await client.post("/photos/", data={"description": "Mountain hike", "tags": "nature,adventure"}, files=files)

    response = await client.get("/photos/search?keyword=Beach&tag=vacation")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["total"] >= 1
    assert any("Beach" in item["description"] for item in res_json["items"])
