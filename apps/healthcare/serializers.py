"""Serializers for healthcare."""

from rest_framework import serializers

from apps.healthcare.models import EmergencyContact, Hospital


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ("id", "user", "name", "phone", "relationship", "is_primary")
        read_only_fields = ("id", "user")


class HospitalSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Hospital
        fields = (
            "id",
            "name",
            "address",
            "location_lat",
            "location_lng",
            "phone",
            "has_psychiatric_emergency",
            "has_pediatric_emergency",
            "has_maternal_emergency",
            "distance_km",
        )


class EmergencyTriggerSerializer(serializers.Serializer):
    location_lat = serializers.FloatField()
    location_lng = serializers.FloatField()
