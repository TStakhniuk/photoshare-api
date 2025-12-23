from enum import Enum

class RoleEnum(str, Enum):
    """
    Enumeration representing the available user roles in the system.
    """
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"