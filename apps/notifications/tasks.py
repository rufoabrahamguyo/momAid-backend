"""Celery tasks for SMS and push placeholders."""

from __future__ import annotations

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import mail_admins

from apps.notifications.utils import format_emergency_message

logger = logging.getLogger(__name__)


@shared_task
def send_otp_sms(phone: str, otp_code: str) -> None:
    """Send OTP via Twilio SMS."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio not configured; OTP for %s: %s", phone, otp_code)
        return
    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        body = f"Your MumAid OTP is: {otp_code}"
        client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone,
        )
    except Exception:
        logger.exception("Failed to send OTP SMS to %s", phone)


@shared_task
def send_emergency_sms(phone: str, user_name: str, location_lat: float, location_lng: float) -> None:
    """Send emergency alert SMS with map link."""
    body = format_emergency_message(user_name, location_lat, location_lng)
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio not configured; emergency SMS would be: %s -> %s", phone, body)
        return
    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=body, from_=settings.TWILIO_PHONE_NUMBER, to=phone)
    except Exception:
        logger.exception("Failed to send emergency SMS to %s", phone)


@shared_task
def send_opportunity_push_notification(opportunity_title: str) -> None:
    """Placeholder for FCM push to admins."""
    logger.info("Push notification placeholder for opportunity: %s", opportunity_title)


@shared_task
def notify_admin_of_interest(opportunity_title: str, user_phone: str) -> None:
    """Notify admins about a new opportunity interest (email MVP)."""
    subject = f"MumAid: interest in {opportunity_title}"
    message = f"User {user_phone} expressed interest in '{opportunity_title}'."
    try:
        mail_admins(subject, message, fail_silently=False)
    except Exception:
        logger.exception("Could not email admins about opportunity interest")
