from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.ratings.schemas import RatingCreate, RatingResponse
from src.ratings import repository as repository_ratings
from src.auth.dependencies import get_current_user, RoleChecker
from src.users.enums import RoleEnum
from src.users.models import User
from src.photos.models import Photo

router = APIRouter(prefix="/ratings", tags=["ratings"])


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
    Allows a user to rate a photo. Users cannot rate their own photos.

    :param photo_id: The ID of the photo to be rated.
    :param body: The rating score (1-5).
    :param db: The database session.
    :param current_user: Currently authenticated user.
    :return: The created rating details.
    """
    sq = select(Photo).filter(Photo.id == photo_id)
    photo_result = await db.execute(sq)
    photo = photo_result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if hasattr(photo, "user_id") and photo.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot rate your own photo")

    existing_rating = await repository_ratings.get_user_rating_for_photo(
        db, photo_id, current_user.id
    )
    if existing_rating:
        raise HTTPException(status_code=409, detail="You have already rated this photo")

    return await repository_ratings.create_rating(
        db, photo_id, current_user.id, body.score
    )


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_rating(
    rating_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MODERATOR])),
):
    """
    Removes a rating. Only admins and moderators have access to this operation.

    :param rating_id: The ID of the rating to delete.
    :param db: The database session.
    :param current_user: User with administrative privileges.
    :return: None
    """
    rating = await repository_ratings.get_rating_by_id(db, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    await repository_ratings.delete_rating(db, rating)
