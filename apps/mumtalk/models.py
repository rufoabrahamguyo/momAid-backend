from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MumTalkPost(BaseModel):  
    title = models.CharField(max_length=255, null=True, blank=True,unique=True)
    content = models.TextField(null=True, blank=True, max_length=300)
    author_hash = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title