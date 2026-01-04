import pytest
from io import BytesIO
from fastapi import status

from src.photos.repository import PhotoRepository
from src.photos.schemas import PhotoCreate
from src.services.cloudinary import CloudinaryService
from src.services.qrcode import QRCodeService
from src.auth.utils import create_access_token
from src.users.repository import create_user
from src.users.schemas import UserCreate
from src.services.cloudinary import AVAILABLE_TRANSFORMATIONS


@pytest.mark.asyncio
async def test_upload_photo(client, test_user, faker, monkeypatch):
    """Test uploading a photo successfully."""

    async def mock_upload_image(file):
        return {"url": "http://fakeurl.com/photo.jpg", "public_id": "fake_public_id"}

    monkeypatch.setattr(CloudinaryService, "upload_image", mock_upload_image)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    file_content = BytesIO(b"fake image bytes")
    response = await client.post(
        "/photos/",
        files={"file": ("photo.jpg", file_content, "image/jpeg")},
        data={"description": faker.sentence(), "tags": "tag1,tag2"},
        headers=headers
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
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id2",
                              photo_data=photo_data)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"description": "new description"}
    response = await client.put(f"/photos/{photo.id}", json=update_data, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "new description"


@pytest.mark.asyncio
async def test_delete_photo(client, test_user, session, faker, monkeypatch):
    """Test deleting a photo successfully."""

    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id3",
                              photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "delete_image", lambda public_id: True)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/photos/{photo.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_transform_photo(client, test_user, session, faker, monkeypatch):
    """Test applying a transformation to a photo."""

    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id4",
                              photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda public_id: "http://url.com/transformed.jpg")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "data:image/png;base64,fakeqrcode")

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    transform_request = {"transformation": "grayscale"}
    response = await client.post(f"/photos/{photo.id}/transform", json=transform_request, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url"] == "http://url.com/transformed.jpg"
    assert "qr_code_url" in data


@pytest.mark.asyncio
async def test_get_photo_transformations(client, test_user, session, faker, monkeypatch):
    """Test fetching all transformations for a photo."""

    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description="desc", tags=[])
    photo = await repo.create(user_id=test_user.id, url="http://url.com/pic.jpg", cloudinary_public_id="id5",
                              photo_data=photo_data)

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda public_id: "http://url.com/trans.jpg")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "data:image/png;base64,fake")

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        f"/photos/{photo.id}/transform",
        json={"transformation": "grayscale"},
        headers=headers
    )

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


@pytest.mark.asyncio
async def test_upload_photo_success(client, test_user, faker, monkeypatch):
    """Test uploading a photo successfully."""

    async def mock_upload_image(file):
        return {"url": "http://fakeurl.com/photo.jpg", "public_id": "fake_public_id"}

    monkeypatch.setattr(CloudinaryService, "upload_image", mock_upload_image)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    file_content = BytesIO(b"fake image bytes")

    response = await client.post(
        "/photos/",
        files={"file": ("photo.jpg", file_content, "image/jpeg")},
        data={"description": faker.sentence(), "tags": "tag1,tag2"},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_upload_photo_invalid_file_type(client, test_user):
    """Test uploading a non-image file (400)."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    file_content = BytesIO(b"text file")

    response = await client.post(
        "/photos/",
        files={"file": ("test.txt", file_content, "text/plain")},
        headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "File must be an image" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_photo_cloudinary_error(client, test_user, monkeypatch):
    """Test upload fail due to Cloudinary error (500)."""

    async def mock_upload_fail(file):
        raise Exception("Cloudinary error")

    monkeypatch.setattr(CloudinaryService, "upload_image", mock_upload_fail)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    file_content = BytesIO(b"img")

    response = await client.post(
        "/photos/",
        files={"file": ("p.jpg", file_content, "image/jpeg")},
        headers=headers
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to upload image" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_photos(client):
    """Test retrieving paginated photos."""
    response = await client.get("/photos/?page=1&size=10")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_search_photos(client):
    """Test search endpoint."""
    response = await client.get("/photos/search?keyword=test&sort_by=created_at")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_photo_by_id(client, test_user, session, faker):
    """Test retrieving a single photo by ID."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id1", PhotoCreate(description="d", tags=[]))
    response = await client.get(f"/photos/{photo.id}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_get_photo_not_found(client):
    """Test retrieving non-existent photo (404)."""
    response = await client.get("/photos/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_photo_success(client, test_user, session):
    """Test updating photo description."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id2", PhotoCreate(description="old", tags=[]))
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.put(f"/photos/{photo.id}", json={"description": "new"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_update_photo_not_found(client, test_user):
    """Test updating non-existent photo (404)."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put("/photos/99999", json={"description": "new"}, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_photo_forbidden(client, session, faker):
    """Test updating another user's photo (403)."""

    victim = await create_user(session, UserCreate(username="victim", email="v@e.com", password="p"))

    hacker = await create_user(session, UserCreate(username="hacker", email="h@e.com", password="p"))

    repo = PhotoRepository(session)
    photo = await repo.create(victim.id, "url", "id_vic", PhotoCreate(description="desc", tags=[]))

    token = create_access_token(data={"sub": hacker.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.put(f"/photos/{photo.id}", json={"description": "hacked"}, headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_photo_success(client, test_user, session, monkeypatch):
    """Test deleting a photo successfully."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id3", PhotoCreate(description="desc", tags=[]))
    monkeypatch.setattr(CloudinaryService, "delete_image", lambda pid: True)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/photos/{photo.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_cloudinary_fail_but_db_success(client, test_user, session, monkeypatch):
    """Test delete proceeds even if Cloudinary fails exception."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id3_fail", PhotoCreate(description="desc", tags=[]))

    def mock_delete_fail(pid):
        raise Exception("Cloudinary fail")

    monkeypatch.setattr(CloudinaryService, "delete_image", mock_delete_fail)

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/photos/{photo.id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_photo_not_found(client, test_user):
    """Test deleting non-existent photo (404)."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete("/photos/99999", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_photo_forbidden(client, session, monkeypatch):
    """Test deleting another user's photo (403)."""

    victim = await create_user(session, UserCreate(username="victim2", email="v2@e.com", password="p"))

    hacker = await create_user(session, UserCreate(username="hacker2", email="h2@e.com", password="p"))

    repo = PhotoRepository(session)
    photo = await repo.create(victim.id, "url", "id_vic2", PhotoCreate(description="desc", tags=[]))

    monkeypatch.setattr(CloudinaryService, "delete_image", lambda pid: True)

    token = create_access_token(data={"sub": hacker.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete(f"/photos/{photo.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_transform_photo_success(client, test_user, session, monkeypatch):
    """Test applying a transformation."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id4", PhotoCreate(description="desc", tags=[]))

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda pid: "http://url.com/t.jpg")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "data:qr")

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(f"/photos/{photo.id}/transform", json={"transformation": "grayscale"}, headers=headers)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_transform_photo_invalid_type(client, test_user, session):
    """Test invalid transformation type (400)."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id4_bad", PhotoCreate(description="desc", tags=[]))

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(f"/photos/{photo.id}/transform", json={"transformation": "invalid_type"},
                                 headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_transform_photo_not_found(client, test_user):
    """Test transforming non-existent photo (404)."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post("/photos/99999/transform", json={"transformation": "grayscale"}, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_photo_transformations(client, test_user, session, monkeypatch):
    """Test fetching transformations."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id5", PhotoCreate(description="desc", tags=[]))

    monkeypatch.setattr(CloudinaryService, "get_grayscale_url", lambda pid: "url")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda url: "qr")
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(f"/photos/{photo.id}/transform", json={"transformation": "grayscale"}, headers=headers)

    response = await client.get(f"/photos/{photo.id}/transformations")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_get_photo_transformations_not_found(client):
    """Test fetching transformations for missing photo (404)."""
    response = await client.get("/photos/99999/transformations")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_photo_qr_code(client, test_user, session):
    """Test getting QR code."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id6", PhotoCreate(description="desc", tags=[]))
    response = await client.get(f"/photos/{photo.id}/qr")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_photo_qr_code_not_found(client):
    """Test getting QR code for missing photo (404)."""
    response = await client.get("/photos/99999/qr")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_user_photos(client, test_user, session, faker):
    """Test retrieving photos by specific user."""
    repo = PhotoRepository(session)
    photo_data = PhotoCreate(description=faker.sentence(), tags=[])
    await repo.create(user_id=test_user.id, url="url", cloudinary_public_id="uid_1", photo_data=photo_data)
    response = await client.get(f"/photos/user/{test_user.id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_upload_photo_exceptions(client, test_user, monkeypatch):
    """Cover HTTP 400 (bad file) and HTTP 500 (upload fail)."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    file_content = BytesIO(b"text")
    response = await client.post(
        "/photos/",
        files={"file": ("test.txt", file_content, "text/plain")},
        headers=headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def mock_fail(file):
        raise Exception("Cloudinary error")

    monkeypatch.setattr(CloudinaryService, "upload_image", mock_fail)

    response = await client.post(
        "/photos/",
        files={"file": ("p.jpg", BytesIO(b"img"), "image/jpeg")},
        headers=headers
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_transform_photo_variations(client, test_user, session, monkeypatch):
    """Test ALL transformation types to cover if/elif branches."""
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id_trans_var", PhotoCreate(description="d", tags=[]))

    monkeypatch.setattr(CloudinaryService, "get_circle_crop_url", lambda p, s: "url")
    monkeypatch.setattr(CloudinaryService, "get_rounded_corners_url", lambda p, r: "url")
    monkeypatch.setattr(CloudinaryService, "get_sepia_url", lambda p: "url")
    monkeypatch.setattr(CloudinaryService, "get_blur_url", lambda p, s: "url")
    monkeypatch.setattr(QRCodeService, "generate_qr_code_data_uri", lambda u: "qr")

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    for trans_type in ["circle", "rounded", "sepia", "blur"]:
        resp = await client.post(
            f"/photos/{photo.id}/transform",
            json={"transformation": trans_type},
            headers=headers
        )
        assert resp.status_code == status.HTTP_200_OK

    resp = await client.post(
        f"/photos/{photo.id}/transform",
        json={"transformation": "invalid_type"},
        headers=headers
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_not_found_errors(client, test_user):
    """Cover all 404 Not Found branches in routes."""
    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}
    fake_id = 999999

    assert (await client.get(f"/photos/{fake_id}")).status_code == 404

    assert (await client.put(f"/photos/{fake_id}", json={"description": "x"}, headers=headers)).status_code == 404

    assert (await client.delete(f"/photos/{fake_id}", headers=headers)).status_code == 404

    assert (await client.post(f"/photos/{fake_id}/transform", json={"transformation": "sepia"},
                              headers=headers)).status_code == 404

    assert (await client.get(f"/photos/{fake_id}/transformations")).status_code == 404

    assert (await client.get(f"/photos/{fake_id}/qr")).status_code == 404


@pytest.mark.asyncio
async def test_permission_errors(client, session):
    """Cover 403 Forbidden branches (editing/deleting other's photo)."""
    owner = await create_user(session, UserCreate(username="owner", email="o@x.com", password="p"))
    repo = PhotoRepository(session)
    photo = await repo.create(owner.id, "url", "id_perm", PhotoCreate(description="d", tags=[]))

    hacker = await create_user(session, UserCreate(username="hacker", email="h@x.com", password="p"))
    token = create_access_token(data={"sub": hacker.email})
    headers = {"Authorization": f"Bearer {token}"}

    resp_upd = await client.put(f"/photos/{photo.id}", json={"description": "hack"}, headers=headers)
    assert resp_upd.status_code == status.HTTP_403_FORBIDDEN

    resp_del = await client.delete(f"/photos/{photo.id}", headers=headers)
    assert resp_del.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_search_photos_route(client):
    """Simply run the search route to cover it."""
    resp = await client.get("/photos/search?keyword=test")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_transform_photo_unknown_type_error(client, test_user, session, monkeypatch):
    """
    Test that providing an unknown transformation string triggers the specific
    HTTP 400 error in the else block.
    """
    repo = PhotoRepository(session)
    photo = await repo.create(test_user.id, "url", "id_unknown_trans", PhotoCreate(description="d", tags=[]))

    token = create_access_token(data={"sub": test_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    fake_transforms = AVAILABLE_TRANSFORMATIONS.copy()
    fake_transforms["bla_bla_bla"] = "Test Description"

    monkeypatch.setattr("src.photos.routes.AVAILABLE_TRANSFORMATIONS", fake_transforms)

    response = await client.post(
        f"/photos/{photo.id}/transform",
        json={"transformation": "bla_bla_bla"},
        headers=headers
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unknown transformation" in response.json()["detail"]