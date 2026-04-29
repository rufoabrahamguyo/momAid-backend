from django.db import models
import string
import secrets
from datetime import timedelta
from django.utils import timezone
import time
from django.contrib.auth import get_user_model

User = get_user_model()


class InviteCode(models.Model):
    creator = models.OneToOneField(User, on_delete=models.CASCADE, related_name="active_code")
    code = models.CharField(unique=True, max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=2)

        if not self.code:
            self.code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        super().save(*args,**kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.code} (For: {self.creator.email})"


class PartnerTask(models.Model):
    CATEGORY_CHOICES = [
        ('health', 'Health & Nutrition'),
        ('logistics', 'Planning & Logistics'),
        ('emotional', 'Emotional Support'),
        ('prep', 'Nursery & Gear'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    why_it_matters = models.TextField(blank=True, null=True) 
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='logistics')
    baby_age_weeks_min = models.IntegerField()
    baby_age_weeks_max = models.IntegerField()
    is_recurring = models.BooleanField(default=False)

    icon = models.CharField(max_length=10, default="🤝")
    estimated_time = models.CharField(max_length=20, blank=True) 
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    @property
    def trimester_label(self):
        if self.baby_age_weeks_max <= 12:
            return "Trimester 1"
        elif self.baby_age_weeks_max <= 26:
            return "Trimester 2"
        else:
            return "Trimester 3"

    def __str__(self):
        return f"Week {self.baby_age_weeks_min}: {self.title}"


class PartnerTaskCompletion(models.Model):

    partner = models.ForeignKey(
        User,
        on_delete=models.CASCADE, 
        related_name="completions"
    )
    task = models.ForeignKey(
        PartnerTask,
        on_delete=models.CASCADE, related_name="partner_tasks")
    status = models.CharField(max_length=20, default="completed") 
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('partner', 'task')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.partner.email} - {self.task.title}"


    



