import uuid
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash the password using the recommended password hash.
    Args:
        password: str
    Returns:
        str: Hashed password
    """
    return password_hash.hash(password)
    

def verify_password(plain_password: str, hashed_password: str) -> bool:   
    """Verify if the passwords matches.
    Args:
        plain_password: str
        hashed_password: str
    Returns:
        bool: True if the passwords matches, False otherwise
    """
    return password_hash.verify(plain_password, hashed_password)


def generate_image_reference() -> str:
    """Generate a unique image reference using UUID4"""
    return str(uuid.uuid4())
