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
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
            "avatar",
            "mother_profile",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
        ]

    def get_avatar(self, obj):
        if not obj.avatar:
            return None
        request = self.context.get("request")
        url = obj.avatar.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url

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
    """PATCH: nested `mother_profile` (mothers only) and/or `avatar` (multipart or JSON with null to clear)."""

    mother_profile = MotherProfilePatchSerializer(required=False, partial=True)

    class Meta:
        model = User
        fields = ("mother_profile", "avatar")
        extra_kwargs = {
            "avatar": {
                "required": False,
                "allow_null": True,
            }
        }

    def validate_avatar(self, value):
        if value and getattr(value, "size", 0) > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image must be 5MB or smaller.")
        return value

    def update(self, instance, validated_data):
        nested = validated_data.pop("mother_profile", None)
        instance = super().update(instance, validated_data)
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