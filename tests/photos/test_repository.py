import pytest
from datetime import datetime, timedelta

from src.photos.repository import PhotoRepository, TagRepository
from src.photos.schemas import PhotoCreate, PhotoUpdate


@pytest.mark.asyncio
async def test_tag_get_or_create(session, faker):
    """Creates a tag or retrieves an existing one."""
    tag_repo = TagRepository(session)
    name = faker.word()
    tag = await tag_repo.get_or_create(name)
    assert tag.id is not None
    tag2 = await tag_repo.get_or_create(name.upper())
    assert tag2.id == tag.id


@pytest.mark.asyncio
async def test_tag_get_or_create_many(session, faker):
    """Creates multiple tags up to a limit of 5."""
    tag_repo = TagRepository(session)
    names = [faker.word() for _ in range(7)]
    tags = await tag_repo.get_or_create_many(names)
    assert len(tags) == 5


@pytest.mark.asyncio
async def test_photo_create_and_get_by_id(session, test_user, faker):
    """Creates a photo and retrieves it by ID."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Test photo", tags=[faker.word()])
    photo = await repo.create(test_user.id, url="http://example.com/1.jpg", cloudinary_public_id="cid1", photo_data=data)
    fetched = await repo.get_by_id(photo.id)
    assert fetched.id == photo.id
    assert fetched.description == "Test photo"


@pytest.mark.asyncio
async def test_photo_update_description(session, test_user, faker):
    """Updates a photo's description."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Old description", tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/2.jpg", cloudinary_public_id="cid2", photo_data=data)
    updated_data = PhotoUpdate(description="New description")
    updated = await repo.update(photo, updated_data)
    assert updated.description == "New description"


@pytest.mark.asyncio
async def test_photo_update_tags(session, test_user, faker):
    """Updates tags of a photo."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Photo with tags", tags=["tag1"])
    photo = await repo.create(test_user.id, url="http://example.com/3.jpg", cloudinary_public_id="cid3", photo_data=data)
    updated = await repo.update_tags(photo, ["tag2", "tag3"])
    tag_names = [t.name for t in updated.tags]
    assert "tag2" in tag_names and "tag3" in tag_names


@pytest.mark.asyncio
async def test_photo_delete(session, test_user, faker):
    """Deletes a photo."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="To delete", tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/4.jpg", cloudinary_public_id="cid4", photo_data=data)
    result = await repo.delete(photo)
    assert result is True
    assert await repo.get_by_id(photo.id) is None


@pytest.mark.asyncio
async def test_photo_search_by_description(session, test_user, faker):
    """Searches photos by description."""
    repo = PhotoRepository(session)
    desc = "Unique description"
    data = PhotoCreate(description=desc, tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/5.jpg", cloudinary_public_id="cid5", photo_data=data)
    results = await repo.search_by_description("Unique")
    assert any(p.id == photo.id for p in results)


@pytest.mark.asyncio
async def test_photo_search_by_tag(session, test_user, faker):
    """Searches photos by tag."""
    repo = PhotoRepository(session)
    tag_name = "specialtag"
    data = PhotoCreate(description="With tag", tags=[tag_name])
    photo = await repo.create(test_user.id, url="http://example.com/6.jpg", cloudinary_public_id="cid6", photo_data=data)
    results = await repo.search_by_tag(tag_name)
    assert any(p.id == photo.id for p in results)


@pytest.mark.asyncio
async def test_photo_get_total_and_user_count(session, test_user, faker):
    """Checks total and user-specific photo counts."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Counting photo", tags=[])
    await repo.create(test_user.id, url="http://example.com/7.jpg", cloudinary_public_id="cid7", photo_data=data)
    total = await repo.get_total_count()
    user_count = await repo.get_user_photos_count(test_user.id)
    assert total >= 1
    assert user_count >= 1


@pytest.mark.asyncio
async def test_photo_search_advanced(session, test_user, faker):
    """Performs advanced search with multiple filters."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Advanced search", tags=["adv"])
    photo = await repo.create(test_user.id, url="http://example.com/8.jpg", cloudinary_public_id="cid8", photo_data=data)
    date_from = datetime.utcnow() - timedelta(days=1)
    photos, total = await repo.search_advanced(keyword="Advanced", tag="adv", user_id=test_user.id, date_from=date_from)
    assert any(p.id == photo.id for p in photos)
    assert total >= 1


@pytest.mark.asyncio
async def test_photo_transformation_create_and_get(session, test_user, faker):
    """Creates a photo transformation and retrieves it."""
    photo_repo = PhotoRepository(session)
    trans_repo = photo_repo.session  # Use same session
    data = PhotoCreate(description="Transform", tags=[])
    photo = await photo_repo.create(test_user.id, url="http://example.com/9.jpg", cloudinary_public_id="cid9", photo_data=data)
    from src.photos.repository import PhotoTransformationRepository
    trans_repo_obj = PhotoTransformationRepository(session)
    transformation = await trans_repo_obj.create(photo.id, url="http://example.com/9_trans.jpg", cloudinary_public_id="trans1", transformation_params='{"blur":5}')
    results = await trans_repo_obj.get_by_photo(photo.id)
    assert any(t.id == transformation.id for t in results)
