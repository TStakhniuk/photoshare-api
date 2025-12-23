from fastapi import FastAPI
from src.auth.routes import router as auth_router
from src.comments.routes import router as comments_router

app = FastAPI(title="PhotoShare API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])


@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to PhotoShare API"}
