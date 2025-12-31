from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.auth.dependencies import get_current_admin_user
from src.users.schemas import UserStatusResponse
from src.users.models import User
from src.users.repository import get_user_by_username, get_user_by_id, toggle_user_active_status

router = APIRouter()


async def _get_user_by_identifier(db: AsyncSession, identifier: str) -> User | None:
    """Helper function to get user by ID (if numeric) or username."""
    try:
        user_id = int(identifier)
        return await get_user_by_id(db, user_id)
    except ValueError:
        return await get_user_by_username(db, identifier)


@router.put("/users/{identifier}/activate", response_model=UserStatusResponse, status_code=status.HTTP_200_OK)
async def activate_user(
    identifier: str,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Administrative endpoint to activate a user account by ID or username.
    
    Only administrators can access this endpoint. Activates a previously deactivated user account,
    allowing them to log in and access protected endpoints again.

    :param identifier: The ID (numeric) or username (string) of the user to activate.
    :param admin_user: The currently authenticated admin user (from JWT token).
    :param db: The database session dependency.
    :return: Updated user information with is_active=True.
    :raises HTTPException: 404 if user is not found, 403 if not admin.
    """
    user = await _get_user_by_identifier(db, identifier)
    
    if not user:
        # Determine if identifier was numeric or string for error message
        try:
            user_id = int(identifier)
            detail = f"User with ID {user_id} not found"
        except ValueError:
            detail = f"User with username '{identifier}' not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own account status"
        )
    
    updated_user = await toggle_user_active_status(db, user, is_active=True)
    
    return UserStatusResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        role=updated_user.role.value,
        created_at=updated_user.created_at
    )


@router.put("/users/{identifier}/deactivate", response_model=UserStatusResponse, status_code=status.HTTP_200_OK)
async def deactivate_user(
    identifier: str,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Administrative endpoint to deactivate (ban) a user account by ID or username.
    
    Only administrators can access this endpoint. Deactivates a user account,
    preventing them from logging in or accessing protected endpoints.

    :param identifier: The ID (numeric) or username (string) of the user to deactivate.
    :param admin_user: The currently authenticated admin user (from JWT token).
    :param db: The database session dependency.
    :return: Updated user information with is_active=False.
    :raises HTTPException: 404 if user is not found, 403 if not admin.
    """
    user = await _get_user_by_identifier(db, identifier)
    
    if not user:
        # Determine if identifier was numeric or string for error message
        try:
            user_id = int(identifier)
            detail = f"User with ID {user_id} not found"
        except ValueError:
            detail = f"User with username '{identifier}' not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own account status"
        )
    
    updated_user = await toggle_user_active_status(db, user, is_active=False)
    
    return UserStatusResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        is_active=updated_user.is_active,
        role=updated_user.role.value,
        created_at=updated_user.created_at
    )

