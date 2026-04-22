import os

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_otp_email(recipient_email, otp):
    from_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", None)
        or getattr(settings, "EMAIL_HOST_USER", None)
        or os.getenv("EMAIL_HOST_USER")
        or "noreply@mumaid.local"
    )
    send_mail(
        subject="Email Verification",
        message=(
            f"This email is valid for 10 minutes. Here is your otp: {otp}. "
            "Please do not share with anyone."
        ),
        from_email=from_email,
        recipient_list=[recipient_email],
        fail_silently=False,
    )
