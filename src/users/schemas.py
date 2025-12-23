from datetime import datetime
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