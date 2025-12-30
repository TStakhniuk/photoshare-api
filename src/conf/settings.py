from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # src/
ROOT_DIR = BASE_DIR.parent                        # project root

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"
    DATABASE_TEST_URL: str = "postgresql+asyncpg://user:password@localhost:5432/postgres_test"
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ROOT_DIR / ".env"
        extra = "ignore"

settings = Settings()

# Cloudinary (отримати на https://cloudinary.com)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
