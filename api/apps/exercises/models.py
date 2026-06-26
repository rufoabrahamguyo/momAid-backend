from core.models import TimeStampedModel
from django.db import models
from cloudinary.models import CloudinaryField


class Exercise(TimeStampedModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    video_file_id = models.CloudinaryField("video", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
