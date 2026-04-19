"""Admin for partner tasks."""

from django.contrib import admin

from apps.partner.models import PartnerTask, PartnerTaskCompletion


@admin.register(PartnerTask)
class PartnerTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "baby_age_weeks_min", "baby_age_weeks_max", "order")


@admin.register(PartnerTaskCompletion)
class PartnerTaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("partner", "task", "completed_at")
