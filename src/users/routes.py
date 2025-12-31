from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.auth.dependencies import get_current_user
from src.users.schemas import UserPublicProfileResponse, UserProfileResponse, UserUpdate
from src.users.models import User
from src.users.repository import get_user_by_username, get_user_by_email, update_user

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Private endpoint for authenticated user to retrieve their own complete profile information.
    
    This endpoint requires authentication and returns full user data including email.
    Only the authenticated user can access their own profile through this endpoint.

    :param current_user: The currently authenticated user (from JWT token).
    :param db: The database session dependency.
    :return: Complete user profile information including email.
    """
    # TODO: Implement photo count when Photo model is available
    # For now, photos_count is set to 0
    # photos_count = await count_user_photos(db, current_user.id)
    
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        photos_count=0
    )


@router.get("/{username}", response_model=UserPublicProfileResponse, status_code=status.HTTP_200_OK)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    """
    Public endpoint to retrieve a user's profile information by username.
    
    This endpoint is accessible to all users (read-only) and returns only public information:
    - Username
    - Registration date
    - Statistics (e.g., photo count)
    
    Does not return sensitive information like email.

    :param username: The unique username of the user.
    :param db: The database session dependency.
    :return: Public user profile information.
    :raises HTTPException: 404 if user is not found.
    """
    user = await get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username '{username}' not found"
        )
    
    # TODO: Implement photo count when Photo model is available
    # For now, photos_count is set to 0
    # photos_count = await count_user_photos(db, user.id)
    
    return UserPublicProfileResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
        photos_count=0
    )


@router.put("/me", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Private endpoint for authenticated user to update their own profile information.
    
    This endpoint requires authentication and allows the user to update:
    - Username (if not already taken)
    - Email (if not already taken)
    
    Users can only update their own profile. The system ensures that:
    - Updated username/email are unique
    - User cannot update other users' profiles

    :param update_data: The data to update (username and/or email).
    :param current_user: The currently authenticated user (from JWT token).
    :param db: The database session dependency.
    :return: Updated user profile information.
    :raises HTTPException: 409 if username or email already exists.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    
    if not update_dict:
        # No fields to update, return current user data
        return UserProfileResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            created_at=current_user.created_at,
            photos_count=0
        )
    
    # Check if username is being updated and if it's already taken
    if "username" in update_dict and update_dict["username"] != current_user.username:
        existing_user = await get_user_by_username(db, update_dict["username"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists"
            )
    
    # Check if email is being updated and if it's already taken
    if "email" in update_dict and update_dict["email"] != current_user.email:
        existing_user = await get_user_by_email(db, update_dict["email"])
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
    
    # Update user data
    updated_user = await update_user(db, current_user, update_dict)
    
    # TODO: Implement photo count when Photo model is available
    # photos_count = await count_user_photos(db, updated_user.id)
    
    return UserProfileResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        created_at=updated_user.created_at,
        photos_count=0
    )
