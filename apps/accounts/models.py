"""Custom user model for MumAid (phone-based authentication)."""

import secrets
from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager for phone-identified users."""

    def create_user(self, phone: str, password: str | None = None, **extra_fields: Any) -> "User":
        if not phone:
            raise ValueError("The phone number must be set")
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone: str, password: str | None = None, **extra_fields: Any) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Application user identified by phone number."""

    class Role(models.TextChoices):
        MOTHER = "mother", "Mother"
        PARTNER = "partner", "Partner"
        ADMIN = "admin", "Admin"

    phone = models.CharField(max_length=20, unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MOTHER)

    support_person_name = models.CharField(max_length=200, blank=True)
    support_person_phone = models.CharField(max_length=20, blank=True)

    ob_name = models.CharField(max_length=200, blank=True)
    ob_phone = models.CharField(max_length=20, blank=True)
    ob_email = models.EmailField(blank=True)

    partner = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_mothers",
    )

    baby_due_date = models.DateField(null=True, blank=True)
    baby_birth_date = models.DateField(null=True, blank=True)

    biometric_enabled = models.BooleanField(default=False)
    push_notifications_enabled = models.BooleanField(default=True)

    unique_code = models.CharField(max_length=16, unique=True, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.role == self.Role.MOTHER and not self.unique_code:
            self.unique_code = secrets.token_hex(4)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.phone)
