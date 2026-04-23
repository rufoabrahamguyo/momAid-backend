import secrets
from django.core.cache import cache
from .tasks import send_otp_email
import requests
from django.conf import settings
from urllib.parse import urlencode
from django.shortcuts import redirect

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


def google_login():
    params = {
        "client_id": settings.CLIENT_GOOGLE_ID,
        "redirect_uri": settings.CLIENT_GOOGLE_REDIRECT,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    return redirect(url)



def get_google_token(code: str):
    url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": settings.CLIENT_GOOGLE_ID,
        "client_secret": settings.CLIENT_GOOGLE_SECRET,
        "redirect_uri": settings.CLIENT_GOOGLE_REDIRECT,
        "grant_type": "authorization_code",
    }

    response = requests.post(url, data=data)

    response_data = response.json()

    if "access_token" not in response_data:
        raise Exception(f"Failed to get token: {response_data}")

    return response_data["access_token"]


def get_google_user_info(access_token: str):
    url = "https://www.googleapis.com/oauth2/v2/userinfo"

    headers = {  
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    if "email" not in response_data:
        raise Exception(f"Failed to fetch user's info: {response_data}")

    return response_data