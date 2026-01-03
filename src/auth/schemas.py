from pydantic import BaseModel


class TokenData(BaseModel):
    """
    Data extracted from a decoded JWT token.
    """
    email: str | None = None


class Token(BaseModel):
    """
    Represents the token response containing access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    """
    Schema for the refresh token request.
    """
    refresh_token: str