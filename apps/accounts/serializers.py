from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MotherProfile, PartnerProfile

User = get_user_model()

# class SupportContactSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SupportContact
#         fields = "__all__"

class MotherProfileSerializer(serializers.ModelSerializer):
    # support_contacts = SupportContactSerializer(many=True, read_only=True)
 
    class Meta:
        model = MotherProfile
        fields = ["baby_due_date", "baby_birth_date", "partner"]

class PartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerProfile
        fields = ["id", "user"]

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_active",
            "joined_at",
            "updated_at",
            "profile", 
        ]

    def get_profile(self, obj):
        if obj.role == 'mother':
            profile = getattr(obj, 'mother_profile', None)
            return MotherProfileSerializer(profile).data if profile else None
        elif obj.role == 'partner':
            profile = getattr(obj, 'partner_profile', None)
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


        if role == 'mother':
            MotherProfile.objects.create(user=user)
        elif role == 'partner':
            PartnerProfile.objects.create(user=user)
            


        return user

