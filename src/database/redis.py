import redis.asyncio as redis
from src.conf.settings import settings

# Global variable for the Redis client
redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    """
    Dependency that provides the Redis client.
    """
    return redis_client



