import pytest
from django.contrib.auth import get_user_model

from apps.accounts import selectors

from .factories import InactiveUserFactory, MotherUserFactory, PartnerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestGetUserByEmail:

    def test_returns_user(self):
        user = MotherUserFactory(email="find@example.com")
        result = selectors.get_user_by_email(email="find@example.com")
        assert result == user

    def test_case_insensitive(self):
        user = MotherUserFactory(email="upper@example.com")
        result = selectors.get_user_by_email(email="UPPER@example.com")
        assert result == user

    def test_strips_whitespace(self):
        user = MotherUserFactory(email="trim@example.com")
        result = selectors.get_user_by_email(email="  trim@example.com  ")
        assert result == user

    def test_returns_none_when_not_found(self):
        assert selectors.get_user_by_email(email="ghost@example.com") is None


@pytest.mark.django_db
class TestGetActiveUserByEmail:

    def test_returns_active_user(self):
        user = MotherUserFactory(email="active@example.com", is_active=True)
        assert selectors.get_active_user_by_email(email="active@example.com") == user

    def test_does_not_return_inactive_user(self):
        InactiveUserFactory(email="inactive@example.com")
        assert selectors.get_active_user_by_email(email="inactive@example.com") is None


@pytest.mark.django_db
class TestUserExists:

    def test_returns_true_when_exists(self):
        MotherUserFactory(email="exists@example.com")
        assert selectors.user_exists(email="exists@example.com") is True

    def test_returns_false_when_not_exists(self):
        assert selectors.user_exists(email="nope@example.com") is False


@pytest.mark.django_db
class TestGetProfiles:

    def test_get_mother_profile(self):
        user = MotherUserFactory()
        profile = selectors.get_mother_profile(user=user)
        assert profile is not None
        assert profile.user == user

    def test_get_mother_profile_returns_none_for_partner(self):
        user = PartnerUserFactory()
        assert selectors.get_mother_profile(user=user) is None

    def test_get_partner_profile(self):
        user = PartnerUserFactory()
        profile = selectors.get_partner_profile(user=user)
        assert profile is not None
        assert profile.user == user

    def test_get_user_with_profile_single_query(self, django_assert_num_queries):
        user = MotherUserFactory()
        with django_assert_num_queries(1):
            result = selectors.get_user_with_profile(user_id=user.id)
        assert result == user
