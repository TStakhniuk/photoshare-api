import pytest
from src.photos.repository import PhotoRepository
from src.photos.schemas import PhotoCreate


@pytest.mark.asyncio
async def test_create_photo(db_session):
    repo = PhotoRepository(db_session)
    photo_data = PhotoCreate(description="Test photo", tags=["test", "unit"])

    photo = await repo.create(
        user_id=1,
        url="http://example.com/test.jpg",
        cloudinary_public_id="test_id",
        photo_data=photo_data
    )

    assert photo.description == "Test photo"
    assert len(photo.tags) == 2