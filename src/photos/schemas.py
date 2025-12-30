"""
Pydantic schemas for Photo and Tag models.
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):
    """Base tag schema."""
    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagResponse(TagBase):
    """Schema for tag response."""
    model_config = ConfigDict(from_attributes=True)

    id: int


class PhotoBase(BaseModel):
    """Base photo schema."""
    description: str | None = Field(None, max_length=1000)


class PhotoCreate(PhotoBase):
    """Schema for creating a photo."""
    tags: list[str] = Field(default_factory=list, max_length=5)


class PhotoUpdate(BaseModel):
    """Schema for updating a photo."""
    description: str | None = Field(None, max_length=1000)


class PhotoResponse(PhotoBase):
    """Schema for photo response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    url: str
    cloudinary_public_id: str
    tags: list[TagResponse] = []
    created_at: datetime
    updated_at: datetime
    average_rating: float | None = None
    ratings_count: int = 0


class PhotoDetailResponse(PhotoResponse):
    """Schema for detailed photo response with user info."""
    username: str | None = None


class PhotoTransformRequest(BaseModel):
    """Schema for photo transformation request."""
    transformation: str = Field(
        ...,
        description="Transformation type: circle, rounded, grayscale, sepia, blur"
    )
    # Optional parameters for specific transformations
    size: int | None = Field(None, ge=50, le=2000, description="Size for circle crop")
    radius: int | None = Field(None, ge=1, le=100, description="Radius for rounded corners")
    blur_strength: int | None = Field(None, ge=1, le=2000, description="Blur strength")


class PhotoTransformResponse(BaseModel):
    """Schema for photo transformation response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_photo_id: int
    url: str
    transformation_params: str | None
    qr_code_url: str | None
    created_at: datetime


class PhotoListResponse(BaseModel):
    """Schema for paginated photo list response."""
    items: list[PhotoResponse]
    total: int
    page: int
    size: int
    pages: int


class PhotoSearchParams(BaseModel):
    """Schema for photo search parameters."""
    keyword: str | None = Field(None, description="Search in description")
    tag: str | None = Field(None, description="Filter by tag name")
    user_id: int | None = Field(None, description="Filter by user ID")
    min_rating: float | None = Field(None, ge=1, le=5, description="Minimum average rating")
    max_rating: float | None = Field(None, ge=1, le=5, description="Maximum average rating")
    date_from: datetime | None = Field(None, description="Photos created after this date")
    date_to: datetime | None = Field(None, description="Photos created before this date")
    sort_by: str = Field("created_at", pattern="^(created_at|rating)$", description="Sort by field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")
