# l4_core/utils/ids.py

import secrets
import string
import uuid


def generate_id(length: int = 12) -> str:
    """Generate a secure, URL-safe ID."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_uuid() -> str:
    """Generate a full UUID4 string."""
    return str(uuid.uuid4())


def generate_long_id() -> str:
    """Generate a longer, more unique ID for DB records."""
    return generate_id(24)
