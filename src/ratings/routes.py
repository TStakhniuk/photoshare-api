from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database.db import get_db
from src.ratings.schemas import RatingCreate, RatingResponse, PhotoAverageRatingResponse
from src.ratings import repository as repository_ratings
from src.photos.repository import PhotoRepository  # Import the class
from src.auth.dependencies import get_current_user, RoleChecker
from src.users.enums import RoleEnum
from src.users.models import User

router = APIRouter()


@router.post(
    "/{photo_id}", response_model=RatingResponse, status_code=status.HTTP_201_CREATED
)
async def add_rating(
    photo_id: int,
    body: RatingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Adds a rating to a photo with checks for self-rating and duplication.

    :param photo_id: The ID of the photo to be rated.
    :param body: The schema containing the score (1-5).
    :param db: The database session dependency.
    :param current_user: The authenticated user performing the action.
    :return: The created rating object.
    """
    # Initialize the Photo repository class
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    # Check if user is trying to rate their own photo
    if photo.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot rate your own photo",
        )

    try:
        return await repository_ratings.create_rating(
            db, photo_id, current_user.id, body.score
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already rated this photo",
        )


@router.get("/{photo_id}/average", response_model=PhotoAverageRatingResponse)
async def get_average_rating(photo_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the calculated average rating and total votes for a specific photo.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    avg_rating, total_votes = await repository_ratings.get_average_rating(db, photo_id)

    return PhotoAverageRatingResponse(
        photo_id=photo_id,
        average_rating=round(avg_rating, 2) if avg_rating else 0.0,
        total_votes=total_votes or 0,
    )


@router.get("/{photo_id}", response_model=list[RatingResponse])
async def get_photo_ratings(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MODERATOR])),
):
    """
    Fetches all individual ratings for a photo, accessible only to staff.

    :param photo_id: The ID of the photo.
    :param db: The database session dependency.
    :param current_user: The authenticated admin or moderator.
    :return: A list of all rating objects for the photo.
    """
    photo_repo = PhotoRepository(db)
    photo = await photo_repo.get_by_id(photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found"
        )

    return await repository_ratings.get_ratings_for_photo(db, photo_id)


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MODERATOR])),
):
    """
    Deletes a specific rating, accessible only to staff.

    :param rating_id: The unique ID of the rating to delete.
    :param db: The database session dependency.
    :param current_user: The authenticated admin or moderator.
    :return: None (HTTP 204).
    """
    rating = await repository_ratings.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found"
        )

    await repository_ratings.delete_rating(db, rating)
