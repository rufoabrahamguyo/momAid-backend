"""Postnatal exercise videos."""

from django.db import models


class Exercise(models.Model):
    """A short guided exercise."""

    title = models.CharField(max_length=100)
    description = models.TextField()
    video_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    duration_seconds = models.IntegerField(default=120)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title
