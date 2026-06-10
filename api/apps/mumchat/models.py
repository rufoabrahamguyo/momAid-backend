import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class MumChatPost(BaseModel):
    title = models.CharField(max_length=255, unique=True, null=True, blank=True)
    content = models.TextField(max_length=300, null=True, blank=True)
    author_hash = models.CharField(max_length=64, db_index=True, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Post {self.public_id}"

    @property
    def reply_count(self):
        return self.replies.count()


class MumChatReply(BaseModel):
    content = models.TextField(max_length=300)
    author_replier_hash = models.CharField(max_length=64, db_index=True)
    post = models.ForeignKey(
        MumChatPost, on_delete=models.CASCADE, related_name="replies"
    )
    parent_reply = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply to {self.post.title}"

    @property
    def is_root_reply(self):
        return self.parent_reply is None