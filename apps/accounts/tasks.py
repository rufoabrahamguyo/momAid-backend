from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


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

@shared_task
def cleanup_stale_data():
    limit = timezone.now() - timedelta(hours=48)
    deleted_users,_ = User.objects.filter(is_active=False, joined_at__lte=limit).delete()
    OutstandingToken.objects.filter(expires_at__lte=timezone.now()).delete()
    return f"Purged {deleted_users} inactive users and cleared expired tokens."





