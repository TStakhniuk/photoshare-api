from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.conf.settings import settings

engine = create_async_engine(settings.DB_URL, echo=True)

SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=AsyncSession,)

# Dependency for session injection
async def get_db():
    async with SessionLocal() as session:
        yield session