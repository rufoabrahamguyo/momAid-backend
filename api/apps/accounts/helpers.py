import secrets

from django.conf import settings
from django.core.cache import cache
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from .tasks import send_otp_email


def generate_email_otp(email: str) -> str:
    email = email.strip().lower()
    otp = str(secrets.randbelow(900000) + 100000)
    cache.set(f"otp:{email}", otp, timeout=600)

    if getattr(settings, "EMAIL_USE_CELERY", False):
        send_otp_email.delay(email, otp)
    else:
        send_otp_email(email, otp)

    return otp


def verify_email_otp(email: str, user_otp: str) -> bool:
    email = email.strip().lower()
    stored_otp = cache.get(f"otp:{email}")

    if stored_otp and stored_otp == str(user_otp):
        cache.delete(f"otp:{email}")
        return True
    return False


def resend_otp(email: str) -> str:
    email = email.strip().lower()

    cache.delete(f"otp:{email}")

    return generate_email_otp(email)


def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.CLIENT_GOOGLE_ID
        )
        return idinfo
    except ValueError:
        return None
