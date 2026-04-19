"""Serializers for accounts and authentication."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Read/update profile for the authenticated user."""

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "role",
            "support_person_name",
            "support_person_phone",
            "ob_name",
            "ob_phone",
            "ob_email",
            "partner_id",
            "unique_code",
            "baby_due_date",
            "baby_birth_date",
            "biometric_enabled",
            "push_notifications_enabled",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "phone", "role", "partner_id", "unique_code", "created_at", "updated_at")


class RegisterSerializer(serializers.Serializer):
    """Request OTP for the given phone number."""

    phone = serializers.CharField(max_length=20)


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP and issue an auth token."""

    phone = serializers.CharField(max_length=20)
    otp = serializers.CharField(max_length=10, write_only=True)
