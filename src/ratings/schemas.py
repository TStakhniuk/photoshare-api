from pydantic import BaseModel, Field, ConfigDict


class RatingCreate(BaseModel):
    """Schema for creating a new rating with validation for score range (1-5)."""

    score: int = Field(ge=1, le=5)


class RatingResponse(BaseModel):
    """Schema for returning rating details including user and photo IDs."""

    id: int
    score: int
    user_id: int
    photo_id: int

    model_config = ConfigDict(from_attributes=True)


class PhotoAverageRatingResponse(BaseModel):
    """Schema for returning the calculated average rating for a photo."""

    photo_id: int
    average_rating: float
    total_votes: int
