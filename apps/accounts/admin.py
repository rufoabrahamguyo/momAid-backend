"""Django admin for accounts."""

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    UserChangeForm as AuthUserChangeForm,
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(AuthUserChangeForm):
    class Meta(AuthUserChangeForm.Meta):
        model = User
        fields = "__all__"


class UserCreateForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = (User.USERNAME_FIELD, "role", "is_staff", "is_active")
        field_classes = {User.USERNAME_FIELD: forms.EmailField}

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("A user with this email address already exists."))
        return User.objects.normalize_email(email)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreateForm

    ordering = ("email",)
    list_display = (
        "email",
        "role",
        "is_staff",
        "is_active",
        "is_superuser",
        "last_login",
        "id",
    )
    list_filter = ("is_staff", "is_active", "is_superuser", "role")
    search_fields = ("email",)
    readonly_fields = ("id", "last_login", "joined_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (_("Account"), {"fields": ("role",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "joined_at", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
