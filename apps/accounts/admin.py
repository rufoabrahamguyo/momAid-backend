"""Django admin for accounts."""

from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = (
        "phone",
        "role",
        "is_staff",
        "is_active",
        "unique_code",
        "created_at",
    )
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("phone", "support_person_phone", "ob_phone", "ob_email")
    readonly_fields = ("created_at", "updated_at", "unique_code", "last_login")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Profile", {"fields": ("role", "partner", "unique_code")}),
        (
            "Support & OB",
            {"fields": ("support_person_name", "support_person_phone", "ob_name", "ob_phone", "ob_email")},
        ),
        ("Baby", {"fields": ("baby_due_date", "baby_birth_date")}),
        ("Preferences", {"fields": ("biometric_enabled", "push_notifications_enabled")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    filter_horizontal = ("groups", "user_permissions")
