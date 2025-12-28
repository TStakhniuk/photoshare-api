import pytest
from typing import AsyncGenerator
from faker import Faker

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from fakeredis import aioredis

from src.database.base import Base
from src.database.db import get_db
from src.database.redis import get_redis
from src.main import app
from src.conf.settings import settings

TEST_DATABASE_URL = settings.DATABASE_TEST_URL

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture(scope="function")
async def init_db():
    """Initializes the database schema and default roles before each test, ensuring a clean state by dropping tables afterwards."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(
            "INSERT INTO roles (id, name) VALUES (1, 'admin'), (2, 'moderator'), (3, 'user')"
        ))
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def session(init_db) -> AsyncGenerator[AsyncSession, None]:
    """Provides an asynchronous database session context for interacting directly with the database during tests."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def mock_redis():
    """Creates an isolated FakeRedis instance and overrides the application's Redis dependency for the duration of the test."""
    redis_instance = aioredis.FakeRedis(decode_responses=True)

    async def override_get_redis():
        yield redis_instance

    app.dependency_overrides[get_redis] = override_get_redis

    yield redis_instance

    await redis_instance.close()
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture(scope="function")
async def client(init_db, mock_redis) -> AsyncGenerator[AsyncClient, None]:
    """Yields an asynchronous HTTP client for integration testing with properly configured database and Redis overrides."""
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def faker():
    """Returns a Faker instance for generating random test data."""
    return Faker()


@pytest.fixture(scope="function")
def user_data(faker):
    """Generates a dictionary containing random user credentials for registration tests."""
    return {
        "username": faker.user_name(),
        "email": faker.email(),
        "password": "password123"
    }