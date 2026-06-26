import logging
import secrets

import cloudinary.uploader
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from . import tasks
from .models import MotherProfile, PartnerProfile
from .selectors import get_user_by_email

User = get_user_model()
logger = logging.getLogger(__name__)


OTP_TTL = 600
OTP_DIGITS = 6


def _otp_cache_key(email: str) -> str:
    return f"otp:{email.strip().lower()}"


def generate_and_send_otp(*, email: str) -> None:
    """Generate a 6-digit OTP, store in cache, fire email task."""
    otp = str(secrets.randbelow(900_000) + 100_000)
    cache.set(_otp_cache_key(email), otp, timeout=OTP_TTL)
    tasks.send_otp_email(email, otp)


def verify_otp(*, email: str, otp: str) -> bool:
    """Return True and delete OTP if valid, False otherwise."""
    key = _otp_cache_key(email)
    stored = cache.get(key)
    if stored and stored == str(otp):
        cache.delete(key)
        return True
    return False


def resend_otp(*, email: str) -> None:
    cache.delete(_otp_cache_key(email))
    generate_and_send_otp(email=email)


@transaction.atomic
def register_user(*, email: str, password: str, role: str) -> User:
    """
    Create user + profile in one transaction, send OTP.
    User starts inactive — activated after OTP verification.
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        role=role,
        is_active=False,
    )

    if role == User.Role.MOTHER:
        MotherProfile.objects.create(user=user)
    elif role == User.Role.PARTNER:
        PartnerProfile.objects.create(user=user)

    generate_and_send_otp(email=user.email)
    return user


def activate_user(*, email: str, otp: str) -> tuple[User, dict]:
    """
    Verify OTP, activate user, return user + JWT tokens.
    Raises ValueError on bad credentials.
    """
    user = get_user_by_email(email=email)

    if not user or not verify_otp(email=email, otp=otp):
        raise ValueError("Invalid email or verification code.")

    user.is_active = True
    user.save(update_fields=["is_active"])

    return user, _make_tokens(user)


def logout_user(*, refresh_token: str) -> None:
    """Blacklist the refresh token. Raises TokenError on invalid token."""
    from rest_framework_simplejwt.tokens import RefreshToken

    token = RefreshToken(refresh_token)
    token.blacklist()


@transaction.atomic
def google_login(*, token: str) -> tuple[User, dict, bool]:
    """
    Verify Google ID token, get-or-create user, return (user, tokens, created).
    Raises ValueError if token is invalid.
    """
    from django.conf import settings
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.CLIENT_GOOGLE_ID,
        )
    except ValueError:
        raise ValueError("Invalid Google token.")

    email = idinfo.get("email")
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"role": User.Role.MOTHER, "is_active": True},
    )
    if not created:
        user.is_active = True
        user.save(update_fields=["is_active"])

    if created:
        MotherProfile.objects.create(user=user)

    return user, _make_tokens(user), created


def update_user_profile(*, user: User, data: dict) -> User:
    for field, value in data.items():
        setattr(user, field, value)
    user.save(update_fields=list(data.keys()))
    return user


def update_mother_profile(*, user: User, data: dict) -> MotherProfile:
    profile = getattr(user, "mother_profile", None)
    if not profile:
        raise ValueError("Mother profile not found.")
    for field, value in data.items():
        setattr(profile, field, value)
    profile.save(update_fields=list(data.keys()))
    return profile


MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}


def upload_profile_image(*, user: User, file) -> str:
    """
    Upload to Cloudinary, persist public_id on user, return secure URL.
    Raises ValueError on validation failure.
    """
    if file.size > MAX_UPLOAD_SIZE:
        raise ValueError("File size exceeds 5 MB limit.")
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError("Unsupported file type. Use JPEG or PNG.")

    result = cloudinary.uploader.upload(
        file,
        folder="profile_pics/",
        public_id=f"user_{user.id}",
        overwrite=True,
        resource_type="image",
    )
    user.image = result["public_id"]
    user.save(update_fields=["image"])
    return result["secure_url"]


def _make_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
