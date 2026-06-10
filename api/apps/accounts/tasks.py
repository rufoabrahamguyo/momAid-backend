import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
    name="accounts.send_otp_email",
)
def send_otp_email(self, recipient_email: str, otp: str) -> None:
    """Send OTP verification email."""
    html = render_to_string("emails/otp_email.html", {"otp": otp})
    msg = EmailMessage(
        subject="Verify your MomAid account",
        body=html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    msg.content_subtype = "html"
    msg.send()
    logger.info("OTP email sent to %s", recipient_email)


@shared_task(
    name="accounts.cleanup_expired_tokens",
    bind=True,
)
def cleanup_expired_tokens(self) -> None:

    from django.utils import timezone
    from rest_framework_simplejwt.token_blacklist.models import (
        OutstandingToken,
    )

    deleted, _ = OutstandingToken.objects.filter(expires_at__lt=timezone.now()).delete()
    logger.info("Cleaned up %d expired tokens", deleted)
