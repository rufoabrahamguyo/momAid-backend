from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.db import models


class UserManager(BaseUserManager):
    """Manager for email users."""

    def create_user(self, email,  password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        MOTHER = "mother", "Mother"
        PARTNER = "partner", "Partner"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=50, unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=Role.choices)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/",
        blank=True,
        null=True,
        help_text="Profile photo (mobile clients: PATCH profile as multipart/form-data with photo file).",
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).only("avatar").first()
            if previous and previous.avatar:
                if not self.avatar or (
                    self.avatar and previous.avatar.name != self.avatar.name
                ):
                    previous.avatar.delete(save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class MotherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mother_profile")

    baby_due_date = models.DateField(null=True, blank=True)
    baby_birth_date = models.DateField(null=True, blank=True)

    partner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_mothers",
        limit_choices_to={"role": User.Role.PARTNER},
    )

    push_notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Mother Profile: {self.user.email}"


class SupportContact(models.Model):
    class ContactType(models.TextChoices):
        PERSONAL = "personal", "Personal Support"
        OB = "ob", "Obstetrician"

    mother = models.ForeignKey(
        MotherProfile,
        on_delete=models.CASCADE,
        related_name="support_contacts"
    )

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    type = models.CharField(max_length=20, choices=ContactType.choices)

    def __str__(self):
        return f"{self.name} ({self.type})"