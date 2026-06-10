from __future__ import annotations

import hashlib
import math

from django.conf import settings


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 points in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return r * 2 * math.asin(min(1.0, math.sqrt(a)))


def maps_link(lat: float, lng: float) -> str:
    """Google Maps URL for a coordinate pair."""
    return f"https://www.google.com/maps?q={lat},{lng}"


def format_emergency_message(user_name: str, lat: float, lng: float) -> str:
    """Build emergency SMS body with a maps link."""
    return f"MomAid emergency: {user_name} needs help. Location: {maps_link(lat, lng)}"


def hash_user_identity(user_id: int) -> str:
    """
    Deterministic anonymous identifier for a user.
    Used for analytics and mumtalk anonymous mode.
    Requires ANONYMOUS_SALT in settings.
    """
    salt = settings.ANONYMOUS_SALT
    if not salt:
        raise ValueError("ANONYMOUS_SALT must be set in settings.")
    return hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()
