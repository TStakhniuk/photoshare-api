from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a plain password matches the hashed password.

    :param plain_password: The raw password provided by the user.
    :param hashed_password: The hashed password stored in the database.
    :return: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generates a secure hash for a plain password.

    :param password: The raw password to hash.
    :return: The hashed version of the password.
    """
    return pwd_context.hash(password)
