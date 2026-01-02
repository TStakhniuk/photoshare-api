import pytest
from sqlalchemy.exc import IntegrityError
from src.ratings import repository as repo_ratings


@pytest.mark.asyncio
async def test_create_rating(session, test_user, test_photo):
    """Tests the successful creation of a new rating record."""
    score = 5
    rating = await repo_ratings.create_rating(
        session, test_photo.id, test_user.id, score
    )

    assert rating.score == score
    assert rating.user_id == test_user.id
    assert rating.photo_id == test_photo.id


@pytest.mark.asyncio
async def test_create_duplicate_rating(session, test_user, test_photo):
    """Tests that a user cannot rate the same photo more than once due to unique constraint."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)

    with pytest.raises(IntegrityError):
        await repo_ratings.create_rating(session, test_photo.id, test_user.id, 4)


@pytest.mark.asyncio
async def test_get_rating_by_id(session, test_user, test_photo):
    """Tests retrieving a specific rating by its primary key."""
    created = await repo_ratings.create_rating(session, test_photo.id, test_user.id, 4)
    retrieved = await repo_ratings.get_rating_by_id(session, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_get_user_rating_for_photo(session, test_user, test_photo):
    """Tests retrieving a rating for a specific photo by a specific user."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 3)
    rating = await repo_ratings.get_user_rating_for_photo(
        session, test_photo.id, test_user.id
    )

    assert rating is not None
    assert rating.score == 3


@pytest.mark.asyncio
async def test_delete_rating(session, test_user, test_photo):
    """Tests the permanent removal of a rating record from the database."""
    rating = await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)
    await repo_ratings.delete_rating(session, rating)

    retrieved = await repo_ratings.get_rating_by_id(session, rating.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_get_average_rating(session, test_user, test_photo, test_admin_user):
    """Tests the calculation of the average score and total count of ratings for a photo."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)
    await repo_ratings.create_rating(session, test_photo.id, test_admin_user.id, 3)

    avg_score, total_count = await repo_ratings.get_average_rating(
        session, test_photo.id
    )

    assert float(avg_score) == 4.0
    assert total_count == 2


@pytest.mark.asyncio
async def test_get_ratings_for_photo(session, test_user, test_photo):
    """Tests retrieving the full list of rating objects associated with a specific photo."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 4)
    ratings = await repo_ratings.get_ratings_for_photo(session, test_photo.id)

    assert len(ratings) == 1
    assert ratings[0].score == 4
