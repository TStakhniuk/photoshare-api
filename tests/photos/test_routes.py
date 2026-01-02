import pytest
from io import BytesIO
from faker import Faker
from fastapi import status

from src.photos.repository import PhotoRepository
from src.photos.schemas import PhotoCreate, PhotoUpdate, PhotoTransformRequest
from src.services.cloudinary import CloudinaryService
from src.services.qrcode import QRCodeService


@pytest.mark.asyncio
async def test_upload_photo(client, test_user, faker, monkeypatch):
    """Test uploading a photo successfully."""
    
    async def mock_upload_image(file):
        return {"url": "http://fakeurl.com/photo.jpg", "public_id": "fake_public_id"}

    monkeypatch.setattr(CloudinaryService, "upload_image", mock_upload_image)

    file_content = BytesIO(b"fake image bytes")
    response = await client.post(
        "/photos/",
        files={"file": ("photo.jpg", file_content, "image/jpeg")},
        data={"description": faker.sentence(), "tags": "tag1,tag2"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["url"] == "http://fakeurl.com/photo.jpg"
    assert len(data["tags"]) == 2


@pytest.mark.asyncio
async def test_get_photos(client, test_user, faker):
    """Test retrieving paginated photos."""
    
    response = await client.get("/photos/?page=1&size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_photo_by_id(client, test_user, session, faker):
    """Test retrieving a single photo by ID."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description=faker.sentence(), tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id1", photo_data=photo_data)

    response = await client.get(f"/photos/{photo.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == photo.id


@pytest.mark.asyncio
async def test_update_photo(client, test_user, session, faker):
    """Test updating photo description."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="old desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id2", photo_data=photo_data)

    update_data = {"description": "new description"}
    response = await client.put(f"/photos/{photo.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "new description"


@pytest.mark.asyncio
async def test_delete_photo(client, test_user, session, faker, monkeypatch):
    """Test deleting a photo successfully."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id3", photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "delete_image", lambda public_id: True)

    response = await client.delete(f"/photos/{photo.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_transform_photo(client, test_user, session, faker, monkeypatch):
    """Test applying a transformation to a photo."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id4", photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda public_id: "http://url.com/transformed.jpg")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "data:image/png;base64,fakeqrcode")

    transform_request = {"transformation": "grayscale"}
    response = await client.post(f"/photos/{photo.id}/transform", json=transform_request)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url"] == "http://url.com/transformed.jpg"
    assert "qr_code_url" in data


@pytest.mark.asyncio
async def test_get_photo_transformations(client, test_user, session, faker, monkeypatch):
    """Test fetching all transformations for a photo."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id5", photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda public_id: "http://url.com/trans.jpg")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "data:image/png;base64,fake")

    # create transformation
    await client.post(f"/photos/{photo.id}/transform", json={"transformation": "grayscale"})

    response = await client.get(f"/photos/{photo.id}/transformations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_photo_qr_code(client, test_user, session, faker):
    """Test getting QR code for a photo."""
    
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id6", photo_data=photo_data)

    response = await client.get(f"/photos/{photo.id}/qr")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


@pytest.mark.asyncio
async def test_get_user_photos(client, test_user, session, faker):
    """Test retrieving photos by specific user."""
    
    repo = PhotoRepository(session)
    for _ in range(3):
        photo_data = PhotoCreate(description=faker.sentence(), tags=[])
        await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id=f"id_user{_}", photo_data=photo_data)

    response = await client.get(f"/photos/user/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
