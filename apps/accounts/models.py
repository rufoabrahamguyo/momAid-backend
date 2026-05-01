import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from cloudinary.models import CloudinaryField
from datetime import datetime, timedelta
import time
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
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

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        return self.create_user(email, password, **extra_fields)

class BaseModel(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)

    class Meta:
        abstract = True

class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    ROLE_CHOICES = [
        ('mother', 'MOTHER'), 
        ('partner', 'PARTNER'), 
    ]

    email = models.EmailField(max_length=50, unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mother')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = CloudinaryField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class MotherProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mother_profile")
    baby_due_date = models.DateField(null=True, blank=True)
    baby_birth_date = models.DateField(null=True, blank=True)
    
    partner = models.OneToOneField(
        'PartnerProfile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="linked_mother"
    )

    def get_current_mother_week(self):

        if not self.baby_due_date:
            return 1

        today = timezone.now().date()   
        days_remaining = (self.baby_due_date - today).days

        days_pregnant = 280 - days_remaining

        current_week = days_pregnant // 7
        return max(1, min(current_week, 42))

    def __str__(self):
        return f"Mother Profile: {self.user.email}"

class PartnerProfile(BaseModel):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="partner_profile",
        limit_choices_to={'role': 'partner'} 
    )

    def __str__(self):
        return f"Partner email: {self.user.email}"

# class SupportContact(models.Model):
#     class ContactType(models.TextChoices):
#         PERSONAL = "personal", "Personal Support"
#         OB = "ob", "Obstetrician"
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     mother = models.ForeignKey(MotherProfile, on_delete=models.CASCADE, related_name="support_contacts")
#     name = models.CharField(max_length=200)
#     phone = models.CharField(max_length=20, blank=True)
#     email = models.EmailField(blank=True)
#     type = models.CharField(max_length=20, choices=ContactType.choices)

#     def __str__(self):
#         return f"{self.name} ({self.type})"