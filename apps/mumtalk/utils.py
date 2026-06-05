import hashlib
from django.conf import settings

def hash_user_identity(user_id: int) -> str:
    """
    Hashes the user ID with a secret salt to create an anonymous identifier.
    """

    if not settings.ANONYMOUS_SALT:
        raise ValueError("ANONYMOUS_SALT must be set in settings for hashing user identities.")

    salt = f"{settings.ANONYMOUS_SALT}:{user_id}"
    return hashlib.sha256(salt.encode()).hexdigest()

