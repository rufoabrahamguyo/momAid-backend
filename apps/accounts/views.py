"""Authentication views: OTP flow and profile."""

from __future__ import annotations

import hashlib
import random
import re

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from knox.models import AuthToken
from knox.views import LogoutView as KnoxLogoutView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.serializers import RegisterSerializer, UserSerializer, VerifyOTPSerializer
from apps.accounts.throttles import AuthThrottle
from apps.notifications.tasks import send_otp_sms

User = get_user_model()

OTP_CACHE_PREFIX = "otp_hash:"


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\s+", "", phone.strip())


def _hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


class RegisterView(APIView):
    """Send a 6-digit OTP to the given phone (stored hashed in cache)."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request: Request) -> Response:
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = _normalize_phone(ser.validated_data["phone"])
        otp = _generate_otp()
        cache_key = f"{OTP_CACHE_PREFIX}{phone}"
        cache.set(cache_key, _hash_otp(otp), timeout=settings.OTP_EXPIRY_SECONDS)
        send_otp_sms.delay(phone, otp)
        return Response({"detail": "OTP sent."}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """Verify OTP and return a Knox token (creates user if new)."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request: Request) -> Response:
        ser = VerifyOTPSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = _normalize_phone(ser.validated_data["phone"])
        otp = ser.validated_data["otp"].strip()
        cache_key = f"{OTP_CACHE_PREFIX}{phone}"
        stored = cache.get(cache_key)
        if not stored or stored != _hash_otp(otp):
            return Response(
                {"error": "Invalid or expired OTP.", "detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cache.delete(cache_key)
        user, _created = User.objects.get_or_create(
            phone=phone,
            defaults={"role": User.Role.MOTHER},
        )
        token_instance, token = AuthToken.objects.create(user=user)
        data = UserSerializer(user).data
        data["token"] = token
        data["expiry"] = token_instance.expiry
        return Response(data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """Retrieve or update the authenticated user profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        ser = UserSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


class LogoutAPIView(KnoxLogoutView):
    """Invalidate the current Knox token."""

    permission_classes = [IsAuthenticated]
