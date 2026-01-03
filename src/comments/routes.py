from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.comments.schemas import CommentCreate, CommentUpdate, CommentResponse
from src.comments import repository as repository_comments
from src.auth.dependencies import get_current_user, RoleChecker
from src.users.enums import RoleEnum
from src.users.models import User

router = APIRouter()


@router.post(
    "/{photo_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    photo_id: int,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new comment under a specific photo.

    :param photo_id: ID of the photo being commented.
    :param body: Data for the new comment.
    :param db: Database session.
    :param current_user: Currently authenticated user.
    :return: The created comment details.
    """
    return await repository_comments.create_comment(db, photo_id, current_user.id, body)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    body: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates an existing comment. Only the author can perform this action.

    :param comment_id: ID of the comment to update.
    :param body: Updated comment data.
    :param db: Database session.
    :param current_user: Currently authenticated user.
    :return: The updated comment details.
    """
    comment = await repository_comments.get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    return await repository_comments.update_comment(db, comment, body)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.MODERATOR])),
):
    """
    Deletes a comment. Only administrators and moderators can perform this action.

    :param comment_id: ID of the comment to delete.
    :param db: Database session.
    :param current_user: User with Admin or Moderator role.
    :return: None
    """
    comment = await repository_comments.get_comment_by_id(db, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    await repository_comments.delete_comment(db, comment)
