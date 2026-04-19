"""Serializers for opportunities."""

from rest_framework import serializers

from apps.opportunities.models import Opportunity, OpportunityInterest


class OpportunitySerializer(serializers.ModelSerializer):
    """Public opportunity payload."""

    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            "id",
            "title",
            "description",
            "deadline",
            "location",
            "eligibility",
            "image",
            "is_filled",
            "created_at",
            "updated_at",
            "is_active",
        )

    def get_is_active(self, obj: Opportunity) -> bool:
        return obj.is_active


class OpportunityWriteSerializer(serializers.ModelSerializer):
    """Create/update opportunity (admin)."""

    class Meta:
        model = Opportunity
        fields = (
            "title",
            "description",
            "deadline",
            "location",
            "eligibility",
            "image",
            "is_filled",
        )


class OpportunityInterestSerializer(serializers.ModelSerializer):
    """Interest record."""

    class Meta:
        model = OpportunityInterest
        fields = ("id", "opportunity", "user", "created_at")
        read_only_fields = ("id", "opportunity", "user", "created_at")
