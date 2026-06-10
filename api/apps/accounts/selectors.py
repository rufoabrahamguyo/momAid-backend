from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import MotherProfile, PartnerProfile

User = get_user_model()


def get_user_by_email(*, email: str) -> User | None:
    return User.objects.filter(email=email.strip().lower()).first()


def get_user_by_id(*, user_id: int) -> User | None:
    return User.objects.filter(id=user_id).first()


def get_active_user_by_email(*, email: str) -> User | None:
    return User.objects.filter(email=email.strip().lower(), is_active=True).first()


def user_exists(*, email: str) -> bool:
    return User.objects.filter(email=email.strip().lower()).exists()


def get_mother_profile(*, user: User) -> MotherProfile | None:
    return (
        MotherProfile.objects.select_related("user", "partner__user")
        .filter(user=user)
        .first()
    )


def get_partner_profile(*, user: User) -> PartnerProfile | None:
    return PartnerProfile.objects.select_related("user").filter(user=user).first()


def get_user_with_profile(*, user_id: int) -> User | None:
    """Single query — fetches user + relevant profile in one shot."""
    return (
        User.objects.select_related("mother_profile", "partner_profile")
        .filter(id=user_id)
        .first()
    )
