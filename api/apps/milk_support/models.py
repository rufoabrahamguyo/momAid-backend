"""Breast milk donation listings."""

from django.conf import settings
from django.db import models


class MilkListing(models.Model):
    """A donor or recipient listing."""

    class ListingType(models.TextChoices):
        DONATE = "donate", "Donating Milk"
        NEED = "need", "Need Milk"

    listing_type = models.CharField(max_length=10, choices=ListingType.choices)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="milk_listings")
    quantity_ml = models.IntegerField()
    location_lat = models.DecimalField(max_digits=10, decimal_places=7)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7)
    location_address = models.CharField(max_length=255)
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.listing_type} {self.quantity_ml}ml"
