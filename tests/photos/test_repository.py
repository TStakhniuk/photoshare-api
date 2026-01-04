import pytest
from datetime import datetime, timedelta, timezone
from src.photos.repository import PhotoRepository, TagRepository
from src.photos.schemas import PhotoCreate, PhotoUpdate
from src.ratings.models import Rating


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
async def test_tag_get_all(session, faker):
    """Test retrieving all tags."""
    tag_repo = TagRepository(session)
    names = [faker.unique.word() for _ in range(3)]
    await tag_repo.get_or_create_many(names)

    tags = await tag_repo.get_all(limit=10)
    assert len(tags) >= 3


@pytest.mark.asyncio
async def test_photo_create_and_get_by_id(session, test_user, faker):
    """Creates a photo and retrieves it by ID."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Test photo", tags=[faker.word()])
    photo = await repo.create(test_user.id, url="http://example.com/1.jpg", cloudinary_public_id="cid1",
                              photo_data=data)
    fetched = await repo.get_by_id(photo.id)
    assert fetched.id == photo.id
    assert fetched.description == "Test photo"
    # Перевірка що рейтинги ініціалізовані пустим списком
    assert fetched.ratings == []


@pytest.mark.asyncio
async def test_photo_update_description(session, test_user, faker):
    """Updates a photo's description."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Old description", tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/2.jpg", cloudinary_public_id="cid2",
                              photo_data=data)
    updated_data = PhotoUpdate(description="New description")
    updated = await repo.update(photo, updated_data)
    assert updated.description == "New description"


@pytest.mark.asyncio
async def test_photo_update_tags(session, test_user, faker):
    """Updates tags of a photo."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Photo with tags", tags=["tag1"])
    photo = await repo.create(test_user.id, url="http://example.com/3.jpg", cloudinary_public_id="cid3",
                              photo_data=data)
    updated = await repo.update_tags(photo, ["tag2", "tag3"])
    tag_names = [t.name for t in updated.tags]
    assert "tag2" in tag_names and "tag3" in tag_names


@pytest.mark.asyncio
async def test_photo_delete(session, test_user, faker):
    """Deletes a photo."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="To delete", tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/4.jpg", cloudinary_public_id="cid4",
                              photo_data=data)
    result = await repo.delete(photo)
    assert result is True
    assert await repo.get_by_id(photo.id) is None


@pytest.mark.asyncio
async def test_photo_search_by_description(session, test_user, faker):
    """Searches photos by description."""
    repo = PhotoRepository(session)
    desc = "Unique description"
    data = PhotoCreate(description=desc, tags=[])
    photo = await repo.create(test_user.id, url="http://example.com/5.jpg", cloudinary_public_id="cid5",
                              photo_data=data)
    results = await repo.search_by_description("Unique")
    assert any(p.id == photo.id for p in results)


@pytest.mark.asyncio
async def test_photo_search_by_tag(session, test_user, faker):
    """Searches photos by tag."""
    repo = PhotoRepository(session)
    tag_name = "specialtag"
    data = PhotoCreate(description="With tag", tags=[tag_name])
    photo = await repo.create(test_user.id, url="http://example.com/6.jpg", cloudinary_public_id="cid6",
                              photo_data=data)
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
async def test_photo_search_advanced_simple(session, test_user, faker):
    """Performs advanced search with simple filters."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Advanced search", tags=["adv"])
    photo = await repo.create(test_user.id, url="http://example.com/8.jpg", cloudinary_public_id="cid8",
                              photo_data=data)
    date_from = datetime.now(timezone.utc) - timedelta(days=1)
    photos, total = await repo.search_advanced(keyword="Advanced", tag="adv", user_id=test_user.id, date_from=date_from)
    assert any(p.id == photo.id for p in photos)
    assert total >= 1


@pytest.mark.asyncio
async def test_photo_search_advanced_complex(session, test_user, faker):
    """Test advanced search with Rating filtering and Sorting."""
    repo = PhotoRepository(session)

    p1 = await repo.create(test_user.id, "u1", "cid_p1", PhotoCreate(description="Photo 1"))  # Rating 5
    p2 = await repo.create(test_user.id, "u2", "cid_p2", PhotoCreate(description="Photo 2"))  # Rating 1
    p3 = await repo.create(test_user.id, "u3", "cid_p3", PhotoCreate(description="Photo 3"))  # No rating (0)

    r1 = Rating(photo_id=p1.id, user_id=test_user.id, score=5)
    r2 = Rating(photo_id=p2.id, user_id=test_user.id, score=1)
    session.add_all([r1, r2])
    await session.commit()

    await session.refresh(p1, ["ratings"])
    await session.refresh(p2, ["ratings"])
    await session.refresh(p3, ["ratings"])

    photos, _ = await repo.search_advanced(sort_by="rating", sort_order="desc")
    assert photos[0].id == p1.id

    photos, _ = await repo.search_advanced(max_rating=2)
    ids = [p.id for p in photos]
    assert p2.id in ids
    assert p3.id in ids
    assert p1.id not in ids

    future = datetime.now(timezone.utc) + timedelta(days=1)
    photos, _ = await repo.search_advanced(date_to=future, sort_order="asc")
    assert photos[0].id == p1.id


@pytest.mark.asyncio
async def test_photo_search_count(session, test_user, faker):
    """Test search_count method covering all filters."""
    repo = PhotoRepository(session)
    data = PhotoCreate(description="Count me", tags=["counttag"])
    await repo.create(test_user.id, "url", "cid_cnt", data)

    count = await repo.search_count(
        keyword="Count",
        tag="counttag",
        user_id=test_user.id,
        date_from=datetime.now(timezone.utc) - timedelta(hours=1),
        date_to=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    assert count >= 1


@pytest.mark.asyncio
async def test_photo_transformation_create_and_get(session, test_user, faker):
    """Creates a photo transformation and retrieves it."""
    photo_repo = PhotoRepository(session)
    data = PhotoCreate(description="Transform", tags=[])
    photo = await photo_repo.create(test_user.id, url="http://example.com/9.jpg", cloudinary_public_id="cid9",
                                    photo_data=data)
    from src.photos.repository import PhotoTransformationRepository
    trans_repo_obj = PhotoTransformationRepository(session)
    transformation = await trans_repo_obj.create(photo.id, url="http://example.com/9_trans.jpg",
                                                 cloudinary_public_id="trans1", transformation_params='{"blur":5}')
    results = await trans_repo_obj.get_by_photo(photo.id)
    assert any(t.id == transformation.id for t in results)


@pytest.mark.asyncio
async def test_photo_search_min_rating_exclusion(session, test_user):
    """
    Test explicitly that photos with low rating are skipped (hits the 'continue' statement).
    """
    repo = PhotoRepository(session)

    p_low = await repo.create(test_user.id, "u_low", "id_low", PhotoCreate(description="Low"))
    session.add(Rating(photo_id=p_low.id, user_id=test_user.id, score=2))
    await session.commit()
    await session.refresh(p_low, ["ratings"])

    photos, total = await repo.search_advanced(min_rating=4)

    assert len(photos) == 0
    assert total == 0