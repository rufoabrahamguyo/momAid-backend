from django.db import models
from core.models import TimeStampedModel


class Exercise(TimeStampedModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file = models.URLField()
    thumbnail_file = models.URLField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
