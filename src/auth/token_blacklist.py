from datetime import datetime, timezone
from jose import jwt, JWTError
import redis.asyncio as redis
from src.conf.settings import settings


async def add_token_to_blacklist(token: str, redis_client: redis.Redis) -> None:
    """
    Adds a JWT token to the Redis blacklist.

    :param token: The JWT token string to blacklist.
    :param redis_client: The Redis client instance.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")

        if exp is None:
            return

        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)

        ttl = int((expires_at - current_time).total_seconds())

        if ttl > 0:
            await redis_client.set(name=f"blacklist:{token}", value="true", ex=ttl)

    except JWTError:
        pass


async def is_token_blacklisted(token: str, redis_client: redis.Redis) -> bool:
    """
    Checks if a token exists in the Redis blacklist.

    :param token: The JWT token string to check.
    :param redis_client: The Redis client instance.
    :return: True if the token is blacklisted, False otherwise.
    """
    is_blacklisted = await redis_client.exists(f"blacklist:{token}")
    return is_blacklisted > 0