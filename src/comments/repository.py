from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.comments.models import Comment
from src.comments.schemas import CommentCreate, CommentUpdate


async def create_comment(
    db: AsyncSession, photo_id: int, user_id: int, body: CommentCreate
) -> Comment:
    """
    Creates a new comment for a specific photo.

    :param db: The database session dependency.
    :param photo_id: The ID of the photo to comment on.
    :param user_id: The ID of the user creating the comment.
    :param body: The schema containing the comment text.
    :return: The newly created Comment object.
    """
    comment = Comment(text=body.text, user_id=user_id, photo_id=photo_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Comment | None:
    """
    Retrieves a single comment by its ID.

    :param db: The database session dependency.
    :param comment_id: The ID of the comment to retrieve.
    :return: The Comment object or None if not found.
    """
    sq = select(Comment).filter(Comment.id == comment_id)
    result = await db.execute(sq)
    return result.scalar_one_or_none()


async def update_comment(
    db: AsyncSession, comment: Comment, body: CommentUpdate
) -> Comment:
    """
    Updates the text of an existing comment.

    :param db: The database session dependency.
    :param comment: The Comment model instance to update.
    :param body: The schema containing the updated text.
    :return: The updated Comment object.
    """
    comment.text = body.text
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment: Comment) -> None:
    """
    Deletes a comment from the database.

    :param db: The database session dependency.
    :param comment: The Comment model instance to delete.
    :return: None
    """
    await db.delete(comment)
    await db.commit()
