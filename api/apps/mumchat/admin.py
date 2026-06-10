from django.contrib import admin

from .models import MumChatPost


@admin.register(MumChatPost)
class MumChatPostAdmin(admin.ModelAdmin):
    list_display = ("public_id", "author_hash", "created_at")
    search_fields = ("content", "author_hash")
    list_filter = ("created_at",)
    readonly_fields = ("public_id", "created_at", "updated_at")
