

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
    mother_profile = MotherProfileSerializer(read_only=True)

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