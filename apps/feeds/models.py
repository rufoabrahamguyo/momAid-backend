from django.db import models
# from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from django.conf import settings

import uuid

User = get_user_model()

class BaseModel(models.Model):
    public_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False, null=True, blank=True)

    class Meta:
        abstract = True

class VideoAttributes(BaseModel):
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    duration = models.FloatField(null=True, blank=True, help_text="Duration in seconds")
    size = models.IntegerField(null=True, blank=True, help_text="Size in bytes")


    def __str__(self):
        return self.title

def get_video_storage():
    storage_class = import_string(settings.VIDEO_STORAGE_BACKEND)
    return storage_class()

class Video(BaseModel):
    video_file = models.FileField(
        upload_to='videos',
        storage=get_video_storage,
        null=True,
        blank=True
    )
    
    attributes = models.OneToOneField(
        VideoAttributes, 
        on_delete=models.CASCADE,
        related_name='video_instance' 
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='videos'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}'s Video: {self.attributes.title}"

class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments",null=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} commented"

    