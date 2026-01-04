import pytest
from jose import jwt
from src.conf.settings import settings
from src.auth.security import verify_password, get_password_hash
from src.auth.utils import create_access_token, decode_token

def test_password_hashing():
    """
    Verifies that password hashing works correctly and that verification logic matches plain passwords with their hashes.
    """
    password = "secret_password"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_token_creation_and_decoding(faker):
    """
    Verifies that a JWT token is created successfully and can be decoded to retrieve the original payload.
    """
    test_email = faker.email()
    data = {"sub": test_email}
    token = create_access_token(data)

    assert isinstance(token, str)

    decoded_data = decode_token(token)
    assert decoded_data is not None
    assert decoded_data.email == test_email

def test_decode_invalid_token():
    """
    Verifies that decoding an invalid token string returns None.
    """
    token = "invalid.token.value"
    decoded_data = decode_token(token)
    assert decoded_data is None

def test_decode_token_no_sub():
    """
    Verifies that decoding a valid JWT that is missing the 'sub' (subject) claim returns None.
    """
    payload = {"data": "some_data"}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    result = decode_token(token)
    assert result is None