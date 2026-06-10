from django.contrib import admin
from .models import PartnerTask, PartnerTaskCompletion, InviteCode


@admin.register(PartnerTask)
class PartnerTaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "baby_age_weeks_min",
        "baby_age_weeks_max",
        "order",
        "is_recurring",
    )
    list_editable = ("order", "is_recurring")  # Change order quickly from the list view
    search_fields = ("title", "description")
    list_filter = ("is_recurring", "baby_age_weeks_min", "baby_age_weeks_max")
    ordering = ("order", "baby_age_weeks_min")


@admin.register(PartnerTaskCompletion)
class PartnerTaskCompletionAdmin(admin.ModelAdmin):
    list_display = ("partner", "task", "status", "completed_at")
    list_filter = ("status", "completed_at")
    search_fields = ("partner__email", "task__title")
    readonly_fields = ("completed_at",)


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "creator", "expires_at", "is_expired")
    readonly_fields = ("code", "expires_at")
    search_fields = ("code", "creator__email")

    def is_expired(self, obj):
        return obj.is_expired

    is_expired.boolean = True
