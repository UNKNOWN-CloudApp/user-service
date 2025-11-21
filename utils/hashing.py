import bcrypt

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Returns the hashed password as a string.
    """
    # Convert password to bytes
    password_bytes = password.encode("utf-8")
    
    # Generate a salt
    salt = bcrypt.gensalt()
    
    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Convert to string for storage in DB
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a plain-text password against the hashed password.
    Returns True if it matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))