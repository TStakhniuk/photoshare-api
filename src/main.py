from fastapi import FastAPI

app = FastAPI(title="PhotoShare API")

@app.get("/")
async def root():
    return {"message": "Welcome to PhotoShare API"}