"""Serializers for remedies."""

from rest_framework import serializers

from apps.remedies.models import BabyCondition, Remedy


class RemedySerializer(serializers.ModelSerializer):
    class Meta:
        model = Remedy
        fields = (
            "id",
            "title",
            "description",
            "duration_minutes",
            "gif_url",
            "order",
        )


class BabyConditionSerializer(serializers.ModelSerializer):
    remedies = RemedySerializer(many=True, read_only=True)

    class Meta:
        model = BabyCondition
        fields = ("id", "name", "icon", "order", "remedies")
