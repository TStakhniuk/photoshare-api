import pytest
from src.ratings.models import Rating


@pytest.mark.asyncio
async def test_add_rating_success(client, test_photo, admin_headers):
    """Verifies that a user can rate a photo that isn't theirs."""
    response = await client.post(
        f"/api/ratings/{test_photo.id}", json={"score": 5}, headers=admin_headers
    )
    assert response.status_code == 201
    assert response.json()["score"] == 5


@pytest.mark.asyncio
async def test_add_rating_self_forbidden(client, auth_headers, test_photo):
    """Ensures a user cannot rate their own photo."""
    response = await client.post(
        f"/api/ratings/{test_photo.id}", json={"score": 5}, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_average_rating(
    client, session, test_photo, test_user, test_admin_user
):
    """Verifies the retrieval of calculated average rating."""
    r1 = Rating(score=5, user_id=test_user.id, photo_id=test_photo.id)
    r2 = Rating(score=3, user_id=test_admin_user.id, photo_id=test_photo.id)
    session.add_all([r1, r2])
    await session.commit()

    response = await client.get(f"/api/ratings/{test_photo.id}/average")
    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.0


@pytest.mark.asyncio
async def test_get_photo_ratings_admin(
    client, session, admin_headers, test_photo, test_user
):
    """Ensures an admin can view all ratings for a photo."""
    rating = Rating(score=5, user_id=test_user.id, photo_id=test_photo.id)
    session.add(rating)
    await session.commit()

    response = await client.get(f"/api/ratings/{test_photo.id}", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_remove_rating_admin(
    client, session, admin_headers, test_photo, test_user
):
    """Verifies that an admin can delete a rating."""
    rating = Rating(score=5, user_id=test_user.id, photo_id=test_photo.id)
    session.add(rating)
    await session.commit()

    response = await client.delete(f"/api/ratings/{rating.id}", headers=admin_headers)
    assert response.status_code == 204
