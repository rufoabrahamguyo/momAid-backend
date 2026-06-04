import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class MumTalkPost(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mumtalk_posts")
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}: {self.content[:40]}"
