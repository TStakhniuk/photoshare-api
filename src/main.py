from fastapi import FastAPI
from src.auth.routes import router as auth_router

app = FastAPI(title="PhotoShare API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to PhotoShare API"}