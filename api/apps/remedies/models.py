"""Baby conditions and remedies."""

from django.db import models


class BabyCondition(models.Model):
    """A baby health topic (e.g. colic)."""

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default="👶")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.name


class Remedy(models.Model):
    """A remedy suggestion under a condition."""

    condition = models.ForeignKey(BabyCondition, on_delete=models.CASCADE, related_name="remedies")
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.IntegerField(null=True, blank=True)
    gif_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Remedies"

    def __str__(self) -> str:
        return self.title
