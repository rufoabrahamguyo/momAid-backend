from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.accounts import services
from apps.accounts.models import MotherProfile, PartnerProfile

from .factories import MotherUserFactory, PartnerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestOTP:

    def test_generate_stores_otp_in_cache(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="otp@example.com")
        assert cache.get("otp:otp@example.com") is not None

    def test_generate_fires_email_task(self):
        with patch("apps.accounts.tasks.send_otp_email") as mock_task:
            services.generate_and_send_otp(email="task@example.com")
        mock_task.assert_called_once()

    def test_otp_is_6_digits(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="digits@example.com")
        otp = cache.get("otp:digits@example.com")
        assert len(otp) == 6
        assert otp.isdigit()

    def test_verify_correct_otp_returns_true(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="verify@example.com")
        otp = cache.get("otp:verify@example.com")
        assert services.verify_otp(email="verify@example.com", otp=otp) is True

    def test_verify_deletes_otp_after_success(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="del@example.com")
        otp = cache.get("otp:del@example.com")
        services.verify_otp(email="del@example.com", otp=otp)
        assert cache.get("otp:del@example.com") is None

    def test_verify_wrong_otp_returns_false(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="wrong@example.com")
        assert services.verify_otp(email="wrong@example.com", otp="000000") is False

    def test_verify_wrong_otp_does_not_delete_stored_otp(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="keep@example.com")
        otp = cache.get("otp:keep@example.com")
        services.verify_otp(email="keep@example.com", otp="000000")
        assert cache.get("otp:keep@example.com") == otp

    def test_resend_replaces_existing_otp(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.generate_and_send_otp(email="resend@example.com")

        with patch("apps.accounts.tasks.send_otp_email"):
            services.resend_otp(email="resend@example.com")

        assert cache.get("otp:resend@example.com") is not None


@pytest.mark.django_db
class TestRegisterUser:

    def test_creates_inactive_user(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            user = services.register_user(
                email="reg@example.com",
                password="securepass123",
                role="mother",
            )
        assert user.is_active is False

    def test_creates_mother_profile_for_mother(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            user = services.register_user(
                email="mum@example.com",
                password="securepass123",
                role="mother",
            )
        assert MotherProfile.objects.filter(user=user).exists()

    def test_does_not_create_partner_profile_for_mother(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            user = services.register_user(
                email="mum2@example.com",
                password="securepass123",
                role="mother",
            )
        assert not PartnerProfile.objects.filter(user=user).exists()

    def test_creates_partner_profile_for_partner(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            user = services.register_user(
                email="dad@example.com",
                password="securepass123",
                role="partner",
            )
        assert PartnerProfile.objects.filter(user=user).exists()

    def test_sends_otp_after_registration(self):
        with patch("apps.accounts.tasks.send_otp_email") as mock_task:
            services.register_user(
                email="otp2@example.com",
                password="securepass123",
                role="mother",
            )

        mock_task.assert_called_once()

    def test_rolls_back_on_failure(self):
        with patch(
            "apps.accounts.models.MotherProfile.objects.create",
            side_effect=Exception("DB error"),
        ):
            with patch("apps.accounts.tasks.send_otp_email"):
                with pytest.raises(Exception):
                    services.register_user(
                        email="rollback@example.com",
                        password="securepass123",
                        role="mother",
                    )

        assert not User.objects.filter(email="rollback@example.com").exists()


@pytest.mark.django_db
class TestActivateUser:

    def test_activates_user(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.register_user(
                email="act@example.com",
                password="securepass123",
                role="mother",
            )

        otp = cache.get("otp:act@example.com")
        activated, _ = services.activate_user(email="act@example.com", otp=otp)

        assert activated.is_active is True

    def test_returns_jwt_tokens(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.register_user(
                email="tok@example.com",
                password="securepass123",
                role="mother",
            )

        otp = cache.get("otp:tok@example.com")
        _, tokens = services.activate_user(email="tok@example.com", otp=otp)

        assert "access" in tokens
        assert "refresh" in tokens

    def test_invalid_otp_raises_value_error(self):
        with patch("apps.accounts.tasks.send_otp_email"):
            services.register_user(
                email="bad@example.com",
                password="securepass123",
                role="mother",
            )

        with pytest.raises(ValueError):
            services.activate_user(email="bad@example.com", otp="000000")

    def test_nonexistent_email_raises_value_error(self):
        with pytest.raises(ValueError):
            services.activate_user(email="ghost@example.com", otp="123456")


@pytest.mark.django_db
class TestLogoutUser:

    def test_blacklists_refresh_token(self):
        user = MotherUserFactory()

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        services.logout_user(refresh_token=str(refresh))

        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

        assert BlacklistedToken.objects.filter(
            token__jti=refresh["jti"]
        ).exists()

    def test_invalid_token_raises_token_error(self):
        from rest_framework_simplejwt.exceptions import TokenError

        with pytest.raises(TokenError):
            services.logout_user(refresh_token="not.a.valid.token")


@pytest.mark.django_db
class TestUpdateUserProfile:

    def test_updates_username(self):
        user = MotherUserFactory(username="old")
        updated = services.update_user_profile(
            user=user,
            data={"username": "new"},
        )
        assert updated.username == "new"

    def test_persists_to_db(self):
        user = MotherUserFactory(username="old")

        services.update_user_profile(
            user=user,
            data={"username": "saved"},
        )

        user.refresh_from_db()
        assert user.username == "saved"


@pytest.mark.django_db
class TestUpdateMotherProfile:

    def test_updates_due_date(self):
        from datetime import date

        user = MotherUserFactory()
        due = date(2025, 12, 1)

        services.update_mother_profile(
            user=user,
            data={"baby_due_date": due},
        )

        user.mother_profile.refresh_from_db()
        assert user.mother_profile.baby_due_date == due

    def test_raises_for_non_mother(self):
        user = PartnerUserFactory()

        with pytest.raises(ValueError, match="Mother profile not found"):
            services.update_mother_profile(
                user=user,
                data={"baby_due_date": None},
            )


@pytest.mark.django_db
class TestUploadProfileImage:

    def _mock_file(self, size=1024, content_type="image/jpeg"):
        f = MagicMock()
        f.size = size
        f.content_type = content_type
        return f

    def test_uploads_and_returns_url(self):
        user = MotherUserFactory()

        with patch(
            "cloudinary.uploader.upload",
            return_value={
                "public_id": "x",
                "secure_url": "https://cdn.example.com/img.jpg",
            },
        ):
            url = services.upload_profile_image(
                user=user,
                file=self._mock_file(),
            )

        assert url == "https://cdn.example.com/img.jpg"

    def test_persists_public_id(self):
        user = MotherUserFactory()

        with patch(
            "cloudinary.uploader.upload",
            return_value={
                "public_id": "profile_pics/user_1",
                "secure_url": "https://x.com/img.jpg",
            },
        ):
            services.upload_profile_image(
                user=user,
                file=self._mock_file(),
            )

        user.refresh_from_db()
        assert str(user.image) == "profile_pics/user_1"

    def test_rejects_oversized_file(self):
        user = MotherUserFactory()

        with pytest.raises(ValueError, match="5 MB"):
            services.upload_profile_image(
                user=user,
                file=self._mock_file(size=10 * 1024 * 1024),
            )

    def test_rejects_invalid_content_type(self):
        user = MotherUserFactory()

        with pytest.raises(ValueError, match="Unsupported"):
            services.upload_profile_image(
                user=user,
                file=self._mock_file(content_type="application/pdf"),
            )