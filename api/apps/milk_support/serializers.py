"""Serializers for milk listings."""

from rest_framework import serializers

from apps.milk_support.models import MilkListing


class MilkListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkListing
        fields = (
            "id",
            "listing_type",
            "user",
            "quantity_ml",
            "location_lat",
            "location_lng",
            "location_address",
            "expiration_date",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "user", "created_at")


class MilkListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkListing
        fields = (
            "listing_type",
            "quantity_ml",
            "location_lat",
            "location_lng",
            "location_address",
            "expiration_date",
            "is_active",
        )
