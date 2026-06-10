from django.db import models

# from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.files.storage import storages
from django.conf import settings

import uuid

User = get_user_model()


class BaseModel(models.Model):
    public_id = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False, null=True, blank=True
    )

    class Meta:
        abstract = True


class VideoAttributes(BaseModel):
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    duration = models.FloatField(
        null=True, blank=True, help_text="Duration in seconds", default=0.0
    )
    size = models.IntegerField(null=True, blank=True, help_text="Size in bytes")

    def __str__(self):
        return self.title


def get_video_storage():
    return storages["default"]


class Video(BaseModel):
    video_file = models.FileField(
        upload_to="videos", storage=get_video_storage, null=True, blank=True
    )

    attributes = models.OneToOneField(
        VideoAttributes, on_delete=models.CASCADE, related_name="video_instance"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="videos")
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}'s Video: {self.attributes.title}"


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="comments", null=True, blank=True
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} commented"


class VideoHistory(BaseModel):
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="watched_history"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="users_history"
    )
    last_watched_at = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["video", "user"]
        ordering = ["-updated_at"]
