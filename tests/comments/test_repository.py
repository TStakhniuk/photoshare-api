import pytest
from src.comments import repository as repo_comments
from src.comments.schemas import CommentCreate, CommentUpdate


@pytest.mark.asyncio
async def test_create_comment(session, test_user, test_photo, faker):
    """Tests the successful creation of a comment."""
    comment_text = faker.sentence()
    body = CommentCreate(text=comment_text)

    comment = await repo_comments.create_comment(
        session, test_photo.id, test_user.id, body
    )

    assert comment.text == comment_text
    assert comment.user_id == test_user.id
    assert comment.photo_id == test_photo.id
    assert comment.id is not None


@pytest.mark.asyncio
async def test_get_comment_by_id(session, test_user, test_photo, faker):
    """Tests retrieving a comment by its unique identifier."""
    body = CommentCreate(text=faker.sentence())
    created = await repo_comments.create_comment(
        session, test_photo.id, test_user.id, body
    )

    retrieved = await repo_comments.get_comment_by_id(session, created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.text == body.text


@pytest.mark.asyncio
async def test_get_comment_not_found(session):
    """Tests retrieving a non-existent comment returns None."""
    retrieved = await repo_comments.get_comment_by_id(session, 999)
    assert retrieved is None


@pytest.mark.asyncio
async def test_update_comment(session, test_user, test_photo, faker):
    """Tests updating the text content of an existing comment."""
    body_create = CommentCreate(text="Original text")
    comment = await repo_comments.create_comment(
        session, test_photo.id, test_user.id, body_create
    )

    new_text = faker.sentence()
    body_update = CommentUpdate(text=new_text)

    updated = await repo_comments.update_comment(session, comment, body_update)

    assert updated.text == new_text
    assert updated.id == comment.id


@pytest.mark.asyncio
async def test_delete_comment(session, test_user, test_photo, faker):
    """Tests the permanent removal of a comment from the database."""
    body = CommentCreate(text=faker.sentence())
    comment = await repo_comments.create_comment(
        session, test_photo.id, test_user.id, body
    )

    await repo_comments.delete_comment(session, comment)

    retrieved = await repo_comments.get_comment_by_id(session, comment.id)
    assert retrieved is None
