from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.ratings.models import Rating


async def create_rating(
    db: AsyncSession, photo_id: int, user_id: int, score: int
) -> Rating:
    """
    Creates a new rating record in the database.

    :param db: The database session dependency.
    :param photo_id: The ID of the photo being rated.
    :param user_id: The ID of the user creating the rating.
    :param score: The rating value (1-5).
    :return: The newly created Rating object.
    """
    rating = Rating(score=score, user_id=user_id, photo_id=photo_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_rating_by_id(db: AsyncSession, rating_id: int) -> Rating | None:
    """
    Retrieves a single rating by its unique ID.

    :param db: The database session dependency.
    :param rating_id: The ID of the rating to retrieve.
    :return: The Rating object or None if not found.
    """
    stmt = select(Rating).filter(Rating.id == rating_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_rating_for_photo(
    db: AsyncSession, photo_id: int, user_id: int
) -> Rating | None:
    """
    Checks if a specific user has already rated a specific photo.

    :param db: The database session dependency.
    :param photo_id: The ID of the photo.
    :param user_id: The ID of the user.
    :return: The existing Rating object or None.
    """
    stmt = select(Rating).filter(Rating.photo_id == photo_id, Rating.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_rating(db: AsyncSession, rating: Rating) -> None:
    """
    Permanently removes a rating from the database.

    :param db: The database session dependency.
    :param rating: The Rating model instance to delete.
    :return: None.
    """
    await db.delete(rating)
    await db.commit()


async def get_average_rating(
    db: AsyncSession, photo_id: int
) -> tuple[float | None, int]:
    """
    Calculates the average rating and total count of votes for a specific photo.

    :return: A tuple containing (average_score, total_count).
    """
    stmt = select(func.avg(Rating.score), func.count(Rating.id)).where(
        Rating.photo_id == photo_id
    )
    result = await db.execute(stmt)
    return result.first()


async def get_ratings_for_photo(db: AsyncSession, photo_id: int) -> list[Rating]:
    """
    Retrieves a list of all ratings associated with a specific photo.

    :param db: The database session dependency.
    :param photo_id: The ID of the photo.
    :return: A list of Rating objects.
    """
    stmt = select(Rating).where(Rating.photo_id == photo_id)
    result = await db.execute(stmt)
    return result.scalars().all()
