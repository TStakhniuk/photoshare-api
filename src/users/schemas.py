from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """
    Base schema for user data containing common attributes.
    """
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """
    Schema for user registration, including the raw password.
    """
    password: str


class UserResponse(UserBase):
    """
    Schema for returning user data (public profile), excluding sensitive info like password.
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True