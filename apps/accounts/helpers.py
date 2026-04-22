import secrets
from django.core.cache import cache
from .tasks import send_otp_email


def generate_email_otp(email: str) -> str:
    email = email.strip().lower()

    otp = str(secrets.randbelow(900000) + 100000)

    cache.set(f"otp:{email}", otp, timeout=600)

    send_otp_email.delay(email, otp)

    return otp


def verify_email_otp(email: str, user_otp: str) -> bool:
    email = email.strip().lower()

    stored_otp = cache.get(f"otp:{email}")

    if stored_otp and stored_otp == str(user_otp):
        cache.delete(f"otp:{email}")
        return True
    return False