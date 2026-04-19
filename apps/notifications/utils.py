"""Helpers for notifications (SMS links, formatting)."""


def maps_link(lat: float, lng: float) -> str:
    """Return a Google Maps URL for coordinates."""
    return f"https://www.google.com/maps?q={lat},{lng}"


def format_emergency_message(user_name: str, lat: float, lng: float) -> str:
    """Build emergency SMS body."""
    link = maps_link(lat, lng)
    return f"MumAid emergency: {user_name} needs help. Location: {link}"
