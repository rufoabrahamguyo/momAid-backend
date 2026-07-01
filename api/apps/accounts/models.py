import uuid

from cloudinary.models import CloudinaryField
from core.models import TimeStampedModel
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
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
        if not extra_fields["is_staff"]:
            raise ValueError("Superuser must have is_staff=True.")
        return self.create_user(email, password, **extra_fields)

def generate_nickname(anonymous_id: str) -> str:
    """Generate a nickname based on the anonymous_id."""
    anonymous_str = str(anonymous_id)
    has_val = int(anonymous_str[0:8], 16)  

    adjectives = ['Brave', 'Clever', 'Swift', 'Mighty', 'Gentle', 'Fierce', 'Wise', 'Bold', 'Noble', 'Lively']
    nouns = ['Lion', 'Tiger', 'Bear', 'Eagle', 'Shark', 'Wolf', 'Panther', 'Falcon', 'Dragon', 'Phoenix']

    adjective = adjectives[has_val % len(adjectives)]
    noun = nouns[(has_val // len(adjectives)) % len(nouns)]

    return f"{adjective}{noun}{has_val % 1000:03d}"
class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        MOTHER = "mother", "Mother"
        PARTNER = "partner", "Partner"
        ADMIN = "admin", "Admin"

    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MOTHER, db_index=True
    )
    image = CloudinaryField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    anonymous_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    nickname = models.CharField(max_length=50, null=True, blank=True)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-joined_at"]

    def save(self, *args, **kwargs):
        self.nickname = generate_nickname(self.anonymous_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    


class MotherProfile(TimeStampedModel):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="mother_profile"
    )
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    baby_due_date = models.DateField(null=True, blank=True)
    baby_birth_date = models.DateField(null=True, blank=True)
    partner = models.OneToOneField(
        "PartnerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_mother",
    )

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Mother Profile"

    def get_current_pregnancy_week(self) -> int:
        """Return the current pregnancy week (1–42). Returns 1 if no due date set."""
        if not self.baby_due_date:
            return 1
        days_remaining = (self.baby_due_date - timezone.now().date()).days
        days_pregnant = 280 - days_remaining
        return max(1, min(days_pregnant // 7, 42))

    def __str__(self):
        return f"MotherProfile({self.user.email})"


class PartnerProfile(TimeStampedModel):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="partner_profile",
        limit_choices_to={"role": User.Role.PARTNER},
    )
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name = "Partner Profile"

    def __str__(self):
        return f"PartnerProfile({self.user.email})"
