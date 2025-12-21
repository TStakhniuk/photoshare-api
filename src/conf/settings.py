from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # src/
ROOT_DIR = BASE_DIR.parent                        # project root

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

    class Config:
        env_file = ROOT_DIR / ".env"
        extra = "ignore"

settings = Settings()
