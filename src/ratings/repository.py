from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.ratings.models import Rating


async def create_rating(
    db: AsyncSession, photo_id: int, user_id: int, score: int
) -> Rating:
    """
    Adds a new rating to a photo.

    :param db: The database session dependency.
    :param photo_id: ID of the photo to rate.
    :param user_id: ID of the user giving the rating.
    :param score: Rating value (1-5).
    :return: The created Rating object.
    """
    rating = Rating(score=score, user_id=user_id, photo_id=photo_id)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return rating


async def get_rating_by_id(db: AsyncSession, rating_id: int) -> Rating | None:
    """
    Retrieves a rating by its ID.

    :param db: The database session dependency.
    :param rating_id: ID of the rating.
    :return: Rating object or None.
    """
    sq = select(Rating).filter(Rating.id == rating_id)
    result = await db.execute(sq)
    return result.scalar_one_or_none()


async def get_user_rating_for_photo(
    db: AsyncSession, photo_id: int, user_id: int
) -> Rating | None:
    """
    Checks if a user has already rated a specific photo.

    :param db: The database session.
    :param photo_id: ID of the photo.
    :param user_id: ID of the user.
    :return: Rating object if exists.
    """
    sq = select(Rating).filter(Rating.photo_id == photo_id, Rating.user_id == user_id)
    result = await db.execute(sq)
    return result.scalar_one_or_none()


async def delete_rating(db: AsyncSession, rating: Rating) -> None:
    """
    Removes a rating from the database.

    :param db: The database session.
    :param rating: Rating instance to delete.
    """
    await db.delete(rating)
    await db.commit()
