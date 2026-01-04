from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from src.users.enums import RoleEnum


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


class RoleResponse(BaseModel):
    """
    Schema for returning role information in responses.
    """
    id: int
    name: str

    class Config:
        from_attributes = True

class UserResponse(UserBase):
    """
    Schema for returning user data (public profile), excluding sensitive info like password.
    """
    id: int
    created_at: datetime
    role: RoleResponse

    class Config:
        from_attributes = True


class UserPublicProfileResponse(BaseModel):
    """
    Schema for public user profile information (read-only).
    Contains only public data visible to all users: username, registration date, and statistics.
    Does not include sensitive information like email.
    """
    id: int
    username: str
    created_at: datetime
    photos_count: int = 0

    class Config:
        from_attributes = True


class UserProfileResponse(UserBase):
    """
    Schema for returning complete user profile information for authenticated user.
    Includes all user data including email (for viewing own profile).
    """
    id: int
    created_at: datetime
    photos_count: int = 0

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """
    Schema for updating user profile information.
    All fields are optional to allow partial updates.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True


class UserStatusResponse(BaseModel):
    """
    Schema for user status response after activation/deactivation.
    """
    id: int
    username: str
    email: str
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True