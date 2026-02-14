# l4_core/utils/ids.py

"""
ID Utilities (L4+)
------------------
Centralized helpers for generating secure, URL‑safe identifiers.

Features:
  - Short IDs (default 12 chars)
  - Long IDs (24 chars)
  - UUID4 generation
  - Future‑proof for typed IDs, prefixes, and sharding
"""

from __future__ import annotations

import secrets
import string
import uuid


# ---------------------------------------------------------
# ALPHABETS
# ---------------------------------------------------------
DEFAULT_ALPHABET = string.ascii_letters + string.digits


# ---------------------------------------------------------
# SHORT ID
# ---------------------------------------------------------
def generate_id(length: int = 12, alphabet: str = DEFAULT_ALPHABET) -> str:
    """
    Generate a secure, URL‑safe random ID.

    Args:
        length: Number of characters in the ID.
        alphabet: Allowed characters (default: A‑Z, a‑z, 0‑9).

    Returns:
        A cryptographically secure random string.
    """
    return "".join(secrets.choice(alphabet) for _ in range(length))


# ---------------------------------------------------------
# LONG ID
# ---------------------------------------------------------
def generate_long_id(length: int = 24) -> str:
    """
    Generate a longer, more unique ID for DB records.

    Args:
        length: Length of the ID (default: 24).

    Returns:
        A secure random string suitable for primary keys.
    """
    return generate_id(length=length)


# ---------------------------------------------------------
# UUID
# ---------------------------------------------------------
def generate_uuid() -> str:
    """
    Generate a full UUID4 string.

    Returns:
        A standard UUID4 string.
    """
    return str(uuid.uuid4())


# ---------------------------------------------------------
# TYPED / PREFIXED IDS (Future‑proof)
# ---------------------------------------------------------
def generate_prefixed_id(prefix: str, length: int = 12) -> str:
    """
    Generate an ID with a prefix, useful for typed identifiers.

    Example:
        "flow_x8F3kLm92aB1"

    Args:
        prefix: The prefix to attach.
        length: Length of the random portion.

    Returns:
        A prefixed secure ID.
    """
    return f"{prefix}_{generate_id(length)}"
