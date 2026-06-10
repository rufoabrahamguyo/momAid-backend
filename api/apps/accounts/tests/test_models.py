import pytest
from datetime import date, timedelta
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model

from apps.accounts.models import MotherProfile, PartnerProfile
from .factories import MotherUserFactory, PartnerUserFactory, MotherProfileFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_str_returns_email(self):
        user = MotherUserFactory()
        assert str(user) == user.email

    def test_email_is_unique(self):
        MotherUserFactory(email="dup@example.com")
        with pytest.raises(IntegrityError):
            MotherUserFactory(email="dup@example.com")

    def test_public_id_is_unique_uuid(self):
        u1 = MotherUserFactory()
        u2 = MotherUserFactory()
        assert u1.public_id != u2.public_id

    def test_default_role_is_mother(self):
        user = User.objects.create_user(email="x@x.com", password="pass")
        assert user.role == User.Role.MOTHER

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@x.com", password="pass")
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == User.Role.ADMIN

    def test_create_user_without_email_raises(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="")

    def test_unusable_password_when_none_given(self):
        user = User.objects.create_user(email="nopw@x.com")
        assert not user.has_usable_password()

    def test_is_active_default_true(self):
        user = MotherUserFactory()
        assert user.is_active is True


@pytest.mark.django_db
class TestMotherProfile:

    def test_str(self):
        profile = MotherProfileFactory()
        assert profile.user.email in str(profile)

    def test_get_current_pregnancy_week_no_due_date(self):
        profile = MotherProfileFactory(baby_due_date=None)
        assert profile.get_current_pregnancy_week() == 1

    def test_get_current_pregnancy_week_midpoint(self):
        # 140 days from now = ~20 weeks remaining = ~20 weeks pregnant
        due = timezone.now().date() + timedelta(days=140)
        profile = MotherProfileFactory(baby_due_date=due)
        week = profile.get_current_pregnancy_week()
        assert 18 <= week <= 22

    def test_get_current_pregnancy_week_clamped_to_42(self):
        # Due date far in the past — should clamp at 42
        due = timezone.now().date() - timedelta(days=200)
        profile = MotherProfileFactory(baby_due_date=due)
        assert profile.get_current_pregnancy_week() == 42

    def test_get_current_pregnancy_week_clamped_to_1(self):
        # Due date far in the future — should clamp at 1
        due = timezone.now().date() + timedelta(days=400)
        profile = MotherProfileFactory(baby_due_date=due)
        assert profile.get_current_pregnancy_week() == 1

    def test_one_to_one_with_user(self):
        profile = MotherProfileFactory()
        assert profile.user.mother_profile == profile

    def test_cascade_delete(self):
        profile = MotherProfileFactory()
        user_id = profile.user.id
        profile.user.delete()
        assert not MotherProfile.objects.filter(user_id=user_id).exists()


@pytest.mark.django_db
class TestPartnerProfile:

    def test_str(self):
        user = PartnerUserFactory()
        assert user.email in str(user.partner_profile)

    def test_one_to_one_with_user(self):
        user = PartnerUserFactory()
        assert user.partner_profile.user == user
