import random
from django.core.cache import cache
from .tasks import send_otp_email

def generate_email_otp(email):
    otp = str(random.randint(100000,999999))
    cache.set(f"otp:{email}", otp, timeout=600)
    send_otp_email.delay(email, otp)

def verify_email_otp(email, user_otp):
    stored_otp = cache.get(f"otp:{email}")

    if stored_otp == user_otp:
        cache.delete(f"otp:{email}")
        return True
    return False