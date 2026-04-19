"""Partner tasks and completions."""

from django.conf import settings
from django.db import models


class PartnerTask(models.Model):
    """Suggested task for a baby age range (weeks)."""

    baby_age_weeks_min = models.IntegerField()
    baby_age_weeks_max = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🤝")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title


class PartnerTaskCompletion(models.Model):
    """Record of a partner completing a task."""

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="partner_task_completions",
        limit_choices_to={"role": "partner"},
    )
    task = models.ForeignKey(PartnerTask, on_delete=models.CASCADE, related_name="completions")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("partner", "task", "completed_at")]

    def __str__(self) -> str:
        return f"{self.partner_id} completed {self.task_id}"
