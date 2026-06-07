import os
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

User = get_user_model()



@shared_task(autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_otp_email(recipient_email, otp):
    html_content = render_to_string("emails/otp_email.html", {"otp": otp})

    message = EmailMessage(
        subject="Verify your account",
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL, 
        to=[recipient_email]
    )

    message.content_subtype = "html" #
    message.send()









