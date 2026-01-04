import pytest
from sqlalchemy.exc import IntegrityError
from src.ratings import repository as repo_ratings
from src.ratings.models import Rating


@pytest.mark.asyncio
async def test_create_rating(session, test_user, test_photo):
    """Test successful creation of a rating with valid data."""
    rating = await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)
    assert rating.id is not None
    assert rating.score == 5


@pytest.mark.asyncio
async def test_create_duplicate_rating(session, test_user, test_photo):
    """Test that creating a second rating for the same photo by the same user raises an IntegrityError."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)

    with pytest.raises(IntegrityError):
        await repo_ratings.create_rating(session, test_photo.id, test_user.id, 4)
    await session.rollback()


@pytest.mark.asyncio
async def test_get_rating_by_id(session, test_user, test_photo):
    """Test retrieving a specific rating record by its unique ID."""
    rating = await repo_ratings.create_rating(session, test_photo.id, test_user.id, 3)
    fetched = await repo_ratings.get_rating_by_id(session, rating.id)
    assert fetched.score == 3


@pytest.mark.asyncio
async def test_get_user_rating_for_photo(session, test_user, test_photo):
    """Test checking if a specific user has already rated a specific photo."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 2)
    fetched = await repo_ratings.get_user_rating_for_photo(session, test_photo.id, test_user.id)
    assert fetched is not None
    assert fetched.score == 2


@pytest.mark.asyncio
async def test_delete_rating(session, test_user, test_photo):
    """Test the permanent deletion of a rating from the database."""
    rating = await repo_ratings.create_rating(session, test_photo.id, test_user.id, 1)
    await repo_ratings.delete_rating(session, rating)
    assert await repo_ratings.get_rating_by_id(session, rating.id) is None


@pytest.mark.asyncio
async def test_get_average_rating(session, test_photo, test_user):
    """Test the calculation of the average score and vote count for a photo."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 4)

    avg, count = await repo_ratings.get_average_rating(session, test_photo.id)
    assert avg == 4.0
    assert count == 1


@pytest.mark.asyncio
async def test_get_ratings_for_photo(session, test_photo, test_user):
    """Test retrieving a list of all ratings associated with a specific photo."""
    await repo_ratings.create_rating(session, test_photo.id, test_user.id, 5)
    ratings = await repo_ratings.get_ratings_for_photo(session, test_photo.id)
    assert len(ratings) == 1
    assert ratings[0].score == 5