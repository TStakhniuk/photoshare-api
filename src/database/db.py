from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.conf.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=AsyncSession,)

# Dependency for session injection
async def get_db():
    """
    Dependency that provides an asynchronous database session.

    Yields a session context manager and ensures the session is closed after the request.

    :yield: AsyncSession attached to the database engine.
    """
    async with SessionLocal() as session:
        yield session