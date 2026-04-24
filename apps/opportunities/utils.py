"""Shared helpers for opportunity views."""


def user_primary_contact_for_admin(user) -> str:
    """Phone if present; otherwise email (User may not have `phone` field)."""
    phone = getattr(user, "phone", None)
    if phone:
        return str(phone)
    return str(getattr(user, "email", "") or user.pk)
