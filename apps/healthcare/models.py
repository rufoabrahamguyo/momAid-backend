"""Emergency contacts and hospitals."""

from django.conf import settings
from django.db import models


class EmergencyContact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "id"]

    def __str__(self) -> str:
        return f"{self.name} ({self.user_id})"


class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    location_lat = models.DecimalField(max_digits=10, decimal_places=7)
    location_lng = models.DecimalField(max_digits=10, decimal_places=7)
    phone = models.CharField(max_length=15)
    has_psychiatric_emergency = models.BooleanField(default=False)
    has_pediatric_emergency = models.BooleanField(default=False)
    has_maternal_emergency = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
