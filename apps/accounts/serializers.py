from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MotherProfile, PartnerProfile

User = get_user_model()

class PartnerProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="public_id"
    )

    class Meta:
        model = PartnerProfile
        fields = [
            "public_id",
            "user",
        ]

class MotherProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="public_id"
    )

    partner = serializers.SlugRelatedField(
        slug_field="public_id",
        queryset=PartnerProfile.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = MotherProfile
        fields = [
            "public_id",
            "user",
            "baby_due_date",
            "baby_birth_date",
            "partner",
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "public_id",
            "email",
            "role",
            "is_active",
            "is_staff",
            "joined_at",
            "updated_at",
            "profile",
        ]

    def get_profile(self, obj):
        if obj.role == "mother":
            profile = getattr(obj, "mother_profile", None)
            return MotherProfileSerializer(profile).data if profile else None

        if obj.role == "partner":
            profile = getattr(obj, "partner_profile", None)
            return PartnerProfileSerializer(profile).data if profile else None

        return None


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        role = validated_data.get("role")

        user = User.objects.create_user(password=password, **validated_data)

        if role == "mother":
            MotherProfile.objects.create(user=user)
        elif role == "partner":
            PartnerProfile.objects.create(user=user)

        return user

