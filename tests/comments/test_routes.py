import pytest
from fastapi import status
from src.comments.models import Comment
from src.users.repository import create_user
from src.users.schemas import UserCreate
from src.auth.utils import create_access_token

@pytest.mark.asyncio
async def test_create_comment(client, auth_headers, test_photo, faker):
    """Verifies that an authorized user can successfully post a comment."""
    text = faker.sentence()
    response = await client.post(
        f"/comments/{test_photo.id}", json={"text": text}, headers=auth_headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["text"] == text

@pytest.mark.asyncio
async def test_update_comment_own(client, session, auth_headers, test_user, test_photo, faker):
    """Verifies that a user can successfully update their own comment."""
    comment = Comment(text="Old text", user_id=test_user.id, photo_id=test_photo.id)
    session.add(comment)
    await session.commit()

    new_text = faker.sentence()
    response = await client.put(
        f"/comments/{comment.id}", json={"text": new_text}, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == new_text

@pytest.mark.asyncio
async def test_update_comment_forbidden(client, session, admin_headers, test_user, test_photo):
    """Ensures a user cannot edit a comment created by another person."""
    comment = Comment(
        text="User's comment", user_id=test_user.id, photo_id=test_photo.id
    )
    session.add(comment)
    await session.commit()

    response = await client.put(
        f"/comments/{comment.id}",
        json={"text": "Admin tries to change this"},
        headers=admin_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_update_comment_not_found(client, auth_headers):
    """Test updating a non-existent comment returns 404."""
    response = await client.put(
        "/comments/99999",
        json={"text": "New text"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_comment_admin(client, session, admin_headers, test_user, test_photo):
    """Verifies that an administrator can delete any comment."""
    comment = Comment(
        text="To be deleted", user_id=test_user.id, photo_id=test_photo.id
    )
    session.add(comment)
    await session.commit()

    response = await client.delete(f"/comments/{comment.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.asyncio
async def test_delete_comment_not_found(client, admin_headers):
    """Test deleting a non-existent comment returns 404."""
    response = await client.delete("/comments/99999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_comment_forbidden_user(client, session, test_user, test_photo, faker):
    """Verifies that a regular user CANNOT delete a comment (only admin/moderator)."""
    regular_user_data = UserCreate(
        username=faker.user_name(),
        email=faker.email(),
        password="password"
    )
    regular_user = await create_user(session, regular_user_data)

    token = create_access_token({"sub": regular_user.email})
    user_headers = {"Authorization": f"Bearer {token}"}

    comment = Comment(
        text="My comment", user_id=test_user.id, photo_id=test_photo.id
    )
    session.add(comment)
    await session.commit()

    response = await client.delete(f"/comments/{comment.id}", headers=user_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN