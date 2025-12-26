from pydantic import BaseModel, Field, ConfigDict


class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    id: int
    score: int
    user_id: int
    photo_id: int

    model_config = ConfigDict(from_attributes=True)


class PhotoAverageRatingResponse(BaseModel):
    photo_id: int
    average_rating: float
    total_votes: int
