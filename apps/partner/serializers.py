"""Serializers for partner flows."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.partner.models import PartnerTask, PartnerTaskCompletion

User = get_user_model()


class ConnectSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=32)


class PartnerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerTask
        fields = (
            "id",
            "baby_age_weeks_min",
            "baby_age_weeks_max",
            "title",
            "description",
            "icon",
            "order",
        )


class PartnerTaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerTaskCompletion
        fields = ("id", "partner", "task", "completed_at")
        read_only_fields = ("id", "partner", "completed_at")
