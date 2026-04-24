"""Opportunities board models."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Opportunity(models.Model):
    """An opportunity posted by staff for mothers."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    location = models.CharField(max_length=200)
    eligibility = models.TextField(blank=True)
    image = models.ImageField(upload_to="opportunities/", blank=True, null=True)
    is_filled = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_opportunities",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_active(self) -> bool:
        return (not self.is_filled) and self.deadline > timezone.now()


class OpportunityInterest(models.Model):
    """A user's interest in an opportunity."""

    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="interests",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact_preference = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="e.g. email, phone, app — how the user prefers follow-up.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("opportunity", "user")]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.opportunity_id}"
