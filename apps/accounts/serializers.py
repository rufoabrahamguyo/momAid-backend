from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import MotherProfile, SupportContact

User = get_user_model()


class SupportContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportContact
        fields = "__all__"


class MotherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherProfile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    mother_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
            "mother_profile",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "joined_at", "updated_at"]

    def get_mother_profile(self, obj):
        try:
            mp = obj.mother_profile
        except MotherProfile.DoesNotExist:
            return None
        return MotherProfileSerializer(mp).data


class MotherProfilePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotherProfile
        fields = ("baby_due_date", "baby_birth_date", "push_notifications_enabled")


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """PATCH body: `{ "mother_profile": { ... } }` (mothers only)."""

    mother_profile = MotherProfilePatchSerializer(required=False, partial=True)

    class Meta:
        model = User
        fields = ("mother_profile",)

    def update(self, instance, validated_data):
        nested = validated_data.get("mother_profile")
        if nested is not None:
            if instance.role != User.Role.MOTHER:
                raise serializers.ValidationError(
                    {"mother_profile": "Only the mother role has a mother_profile here."}
                )
            profile, _ = MotherProfile.objects.get_or_create(user=instance)
            for k, v in nested.items():
                setattr(profile, k, v)
            profile.save()
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create_user(password=password, **validated_data)

        if user.role == User.Role.MOTHER:
            MotherProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = User.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs