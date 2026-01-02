import pytest
from src.comments.models import Comment


@pytest.mark.asyncio
async def test_create_comment(client, auth_headers, test_photo, faker):
    """Verifies that an authorized user can successfully post a comment."""
    text = faker.sentence()
    response = await client.post(
        f"/api/comments/{test_photo.id}", json={"text": text}, headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["text"] == text


@pytest.mark.asyncio
async def test_update_comment_own(
    client, session, auth_headers, test_user, test_photo, faker
):
    """Verifies that a user can successfully update their own comment."""
    comment = Comment(text="Old text", user_id=test_user.id, photo_id=test_photo.id)
    session.add(comment)
    await session.commit()

    new_text = faker.sentence()
    response = await client.put(
        f"/api/comments/{comment.id}", json={"text": new_text}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["text"] == new_text


@pytest.mark.asyncio
async def test_update_comment_forbidden(
    client, session, admin_headers, test_user, test_photo
):
    """Ensures a user cannot edit a comment created by another person."""
    comment = Comment(
        text="User's comment", user_id=test_user.id, photo_id=test_photo.id
    )
    session.add(comment)
    await session.commit()

    response = await client.put(
        f"/api/comments/{comment.id}",
        json={"text": "Admin tries to change this"},
        headers=admin_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_comment_admin(
    client, session, admin_headers, test_user, test_photo
):
    """Verifies that an administrator can delete any comment."""
    comment = Comment(
        text="To be deleted", user_id=test_user.id, photo_id=test_photo.id
    )
    session.add(comment)
    await session.commit()

    response = await client.delete(f"/api/comments/{comment.id}", headers=admin_headers)
    assert response.status_code == 204
