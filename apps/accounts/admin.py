"""Django admin for accounts."""

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ("id",)

    list_display = (
        "id",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_staff", "is_active")

    search_fields = ("id",)

    readonly_fields = ("last_login",)

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login",)}),
    )