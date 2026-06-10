from django.db import models
import uuid


class TimeStampedModel(models.Model):
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(TimeStampedModel):

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_active(self):
        return not self.is_deleted

    def delete(self, using=None, keep_parents=False):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self):
        super().delete()
