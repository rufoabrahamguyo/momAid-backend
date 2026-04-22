from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_otp_email(recipient_email, otp):
    send_mail(
        subject="Email Verification",
        message=(
            f"This email is valid for 10 minutes. "
            f"Here is your OTP: {otp}. "
            "Do not share it."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=False,
    )