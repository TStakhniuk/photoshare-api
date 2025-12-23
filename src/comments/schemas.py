from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CommentCreate(BaseModel):
    """
    Schema for creating a new comment.
    """

    text: str


class CommentUpdate(BaseModel):
    """
    Schema for updating an existing comment's text.
    """

    text: str


class CommentResponse(BaseModel):
    """
    Schema for returning detailed comment information in responses.
    """

    id: int
    text: str
    user_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
