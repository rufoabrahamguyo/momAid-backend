from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model

User = get_user_model()

class VideoAttributes(models.Model):
    title = models.CharField(max_length=50, db_index=True)
    description = models.TextField()
    duration = models.FloatField(null=True, blank=True, help_text="Duration in seconds")
    size = models.IntegerField(null=True, blank=True, help_text="Size in bytes")
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    video_file = CloudinaryField('video', null=True, blank=True, resource_type='video')
    
    attributes = models.OneToOneField(
        VideoAttributes, 
        on_delete=models.CASCADE,
        related_name='video'
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='videos'
    )

    def __str__(self):
        return f"{self.user.email}'s Video: {self.attributes.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} commented"

    