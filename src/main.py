import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.conf.settings import settings
from src.database import redis as redis_db
from src.auth.routes import router as auth_router
from src.comments.routes import router as comments_router
from src.photos.routes import router as photos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager that handles the application startup and shutdown events.
    """
    # Startup
    redis_db.redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    yield
    # Shutdown
    await redis_db.redis_client.close()


app = FastAPI(title="PhotoShare API", lifespan=lifespan)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(photos_router, prefix="/photos", tags=["photos"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])


@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to PhotoShare API"}
