import cloudinary.utils
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import MotherProfile, PartnerProfile

User = get_user_model()


class PartnerProfileSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(source="user.public_id", read_only=True)

    class Meta:
        model = PartnerProfile
        fields = ["public_id", "user"]


class MotherProfileSerializer(serializers.ModelSerializer):
    user    = serializers.UUIDField(source="user.public_id", read_only=True)
    partner = serializers.UUIDField(source="partner.public_id", read_only=True, allow_null=True)
    current_pregnancy_week = serializers.SerializerMethodField()

    class Meta:
        model = MotherProfile
        fields = [
            "public_id",
            "user",
            "baby_due_date",
            "baby_birth_date",
            "partner",
            "current_pregnancy_week",
        ]

    def get_current_pregnancy_week(self, obj) -> int:
        return obj.get_current_pregnancy_week()


class UserSerializer(serializers.ModelSerializer):
    image   = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "public_id",
            "email",
            "username",
            "image",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
            "profile",
        ]

    def get_image(self, obj) -> str | None:
        if not obj.image:
            return None
        try:
            url, _ = cloudinary.utils.cloudinary_url(str(obj.image), secure=True)
            return url
        except Exception:
            return None

    def get_profile(self, obj) -> dict | None:
        if obj.role == User.Role.MOTHER:
            profile = getattr(obj, "mother_profile", None)
            return MotherProfileSerializer(profile).data if profile else None
        if obj.role == User.Role.PARTNER:
            profile = getattr(obj, "partner_profile", None)
            return PartnerProfileSerializer(profile).data if profile else None
        return None




class RegisterSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role     = serializers.ChoiceField(choices=User.Role.choices)

    def validate_email(self, value):
        from .selectors import user_exists
        if user_exists(email=value):
            raise serializers.ValidationError("An account with this email already exists.")
        return value.strip().lower()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp   = serializers.CharField(min_length=6, max_length=6)

    def validate_email(self, value):
        return value.strip().lower()


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]
        extra_kwargs = {"email": {"required": False}}


class UpdateMotherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherProfile
        fields = ["baby_due_date", "baby_birth_date"]