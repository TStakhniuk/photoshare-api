import pytest
from jose import jwt
from src.conf.settings import settings
from src.auth.token_blacklist import add_token_to_blacklist

@pytest.mark.asyncio
async def test_add_invalid_token_to_blacklist(mock_redis):
    """
    Verifies that adding a structurally invalid token to the blacklist handles the exception gracefully (does not crash) and does not store anything in Redis.
    """
    try:
        await add_token_to_blacklist("invalid_garbage_token", mock_redis)
    except Exception as e:
        pytest.fail(f"Function raised exception unexpectedly: {e}")

    keys = await mock_redis.keys("*")
    assert len(keys) == 0

@pytest.mark.asyncio
async def test_blacklist_token_no_exp(mock_redis, faker):
    """
    Verifies that adding a token without an expiration ('exp') claim is ignored and not stored in Redis.
    """
    payload = {"sub": faker.email()}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    await add_token_to_blacklist(token, mock_redis)

    keys = await mock_redis.keys("*")
    assert len(keys) == 0