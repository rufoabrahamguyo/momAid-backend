from celery import shared_task
from django.core.mail import send_mail
import os

@shared_task
def send_otp_email(recipient_email,otp):
    send_mail(
        subject="Email Verification",
        message=f"This email is valid for 10minutes. Here is your otp: {otp}.Please do not share with anyone",
        from_email=os.getenv("EMAIL_HOST_USER"),
        recipient_list=[recipient_email],
        fail_silently=False
    )
