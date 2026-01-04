import pytest
from fastapi import status
from src.ratings.models import Rating
from src.users.schemas import UserCreate
from src.users.repository import create_user
from src.auth.utils import create_access_token


@pytest.mark.asyncio
async def test_add_rating_success(client, test_photo, session, faker):
    """Verifies that a user can rate a photo that isn't theirs."""
    other_user = await create_user(session, UserCreate(username="rater", email="r@e.com", password="p"))
    token = create_access_token(data={"sub": other_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        f"/ratings/{test_photo.id}",
        json={"score": 5},
        headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["score"] == 5


@pytest.mark.asyncio
async def test_add_rating_self_forbidden(client, auth_headers, test_photo):
    """Ensures a user cannot rate their own photo."""
    response = await client.post(
        f"/ratings/{test_photo.id}",
        json={"score": 5},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "cannot rate your own photo" in response.json()["detail"]


@pytest.mark.asyncio
async def test_add_rating_photo_not_found(client, auth_headers):
    """Test rating a non-existent photo."""
    response = await client.post(
        "/ratings/99999",
        json={"score": 5},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_add_rating_duplicate_conflict(client, test_photo, session):
    """Test that rating the same photo twice returns 409 Conflict."""
    rater = await create_user(session, UserCreate(username="rater2", email="r2@e.com", password="p"))
    token = create_access_token(data={"sub": rater.email})
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(f"/ratings/{test_photo.id}", json={"score": 5}, headers=headers)

    response = await client.post(f"/ratings/{test_photo.id}", json={"score": 4}, headers=headers)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already rated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_average_rating(client, session, test_photo):  # <--- ПРИБРАЛИ ЗАЙВУ ФІКСТУРУ
    """Verifies the retrieval of calculated average rating."""
    rater = await create_user(session, UserCreate(username="rater3", email="r3@e.com", password="p"))

    r1 = Rating(score=5, user_id=rater.id, photo_id=test_photo.id)
    session.add(r1)
    await session.commit()

    response = await client.get(f"/ratings/{test_photo.id}/average")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["average_rating"] == 5.0
    assert data["total_votes"] == 1


@pytest.mark.asyncio
async def test_get_average_rating_not_found(client):
    """Test getting average for missing photo."""
    response = await client.get("/ratings/99999/average")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_photo_ratings_admin(client, session, admin_headers, test_photo, test_user):
    """Ensures an admin can view all ratings for a photo."""
    rating = Rating(score=5, user_id=test_user.id, photo_id=test_photo.id)
    session.add(rating)
    await session.commit()

    response = await client.get(f"/ratings/{test_photo.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_photo_ratings_forbidden(client, session, test_photo, faker):
    """Regular user cannot see list of ratings."""

    user = await create_user(session, UserCreate(username="reg_user", email="reg@e.com", password="p"))
    token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get(f"/ratings/{test_photo.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_get_photo_ratings_not_found(client, admin_headers):
    """Admin getting ratings for missing photo."""
    response = await client.get("/ratings/99999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_rating_admin(client, session, admin_headers, test_photo, test_user):
    """Verifies that an admin can delete a rating."""
    rating = Rating(score=5, user_id=test_user.id, photo_id=test_photo.id)
    session.add(rating)
    await session.commit()

    response = await client.delete(f"/ratings/{rating.id}", headers=admin_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_remove_rating_not_found(client, admin_headers):
    """Admin deleting missing rating."""
    response = await client.delete("/ratings/99999", headers=admin_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_remove_rating_forbidden(client, session, test_photo):
    """Regular user cannot delete rating."""

    user = await create_user(session, UserCreate(username="reg_user2", email="reg2@e.com", password="p"))
    token = create_access_token(data={"sub": user.email})
    headers = {"Authorization": f"Bearer {token}"}

    rating = Rating(score=5, user_id=user.id, photo_id=test_photo.id)
    session.add(rating)
    await session.commit()

    response = await client.delete(f"/ratings/{rating.id}", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN