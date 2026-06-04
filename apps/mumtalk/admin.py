from django.contrib import admin

from .models import MumTalkPost


@admin.register(MumTalkPost)
class MumTalkPostAdmin(admin.ModelAdmin):
    list_display = ("public_id", "user", "created_at")
    search_fields = ("content", "user__email")
    list_filter = ("created_at",)
    readonly_fields = ("public_id", "created_at", "updated_at")
