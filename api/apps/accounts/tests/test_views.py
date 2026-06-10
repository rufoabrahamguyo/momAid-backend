import pytest
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch

from apps.accounts import services
from .factories import MotherUserFactory, PartnerUserFactory, InactiveUserFactory


@pytest.mark.django_db
class TestRegisterView:
    url = "/api/auth/v1/register/"

    def test_returns_201_on_success(self, api_client):
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            res = api_client.post(
                self.url,
                {
                    "email": "new@example.com",
                    "password": "securepass123",
                    "role": "mother",
                },
            )
        assert res.status_code == 201

    def test_returns_400_on_duplicate_email(self, api_client):
        MotherUserFactory(email="dup@example.com")
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            res = api_client.post(
                self.url,
                {
                    "email": "dup@example.com",
                    "password": "securepass123",
                    "role": "mother",
                },
            )
        assert res.status_code == 400

    def test_returns_400_on_missing_fields(self, api_client):
        res = api_client.post(self.url, {"email": "x@x.com"})
        assert res.status_code == 400

    def test_returns_400_on_invalid_role(self, api_client):
        res = api_client.post(
            self.url, {"email": "x@x.com", "password": "pass123", "role": "wizard"}
        )
        assert res.status_code == 400

    def test_does_not_require_auth(self, api_client):
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            res = api_client.post(
                self.url,
                {
                    "email": "open@example.com",
                    "password": "securepass123",
                    "role": "mother",
                },
            )
        assert res.status_code != 401


@pytest.mark.django_db
class TestVerifyOTPView:
    url = "/api/auth/v1/verify/token/"

    def test_activates_user_and_returns_tokens(self, api_client):
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            services.register_user(
                email="v@example.com", password="pass123", role="mother"
            )
        otp = cache.get("otp:v@example.com")
        res = api_client.post(self.url, {"email": "v@example.com", "otp": otp})
        assert res.status_code == 200
        assert "access" in res.data
        assert "refresh" in res.data

    def test_returns_401_on_wrong_otp(self, api_client):
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            services.register_user(
                email="bad@example.com", password="pass123", role="mother"
            )
        res = api_client.post(self.url, {"email": "bad@example.com", "otp": "000000"})
        assert res.status_code == 401

    def test_returns_400_on_missing_fields(self, api_client):
        res = api_client.post(self.url, {"email": "x@x.com"})
        assert res.status_code == 400


@pytest.mark.django_db
class TestLoginView:
    url = "/api/auth/v1/login/"

    def test_returns_tokens_on_valid_credentials(self, api_client):
        MotherUserFactory(email="login@example.com", password=None)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(email="login@example.com")
        user.set_password("testpass123")
        user.save()
        res = api_client.post(
            self.url, {"email": "login@example.com", "password": "testpass123"}
        )
        assert res.status_code == 200
        assert "access" in res.data

    def test_returns_401_on_wrong_password(self, api_client):
        MotherUserFactory(email="wrongpw@example.com")
        res = api_client.post(
            self.url, {"email": "wrongpw@example.com", "password": "wrongpass"}
        )
        assert res.status_code == 401

    def test_returns_401_for_inactive_user(self, api_client):
        InactiveUserFactory(email="inactive@example.com")
        res = api_client.post(
            self.url, {"email": "inactive@example.com", "password": "testpass123"}
        )
        assert res.status_code == 401


@pytest.mark.django_db
class TestLogoutView:
    url = "/api/auth/v1/logout/"

    def test_returns_204_on_success(self, auth_client, mother_user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = str(RefreshToken.for_user(mother_user))
        res = auth_client.post(self.url, {"refresh": refresh})
        assert res.status_code == 204

    def test_returns_400_on_missing_token(self, auth_client):
        res = auth_client.post(self.url, {})
        assert res.status_code == 400

    def test_returns_400_on_invalid_token(self, auth_client):
        res = auth_client.post(self.url, {"refresh": "invalid.token.here"})
        assert res.status_code == 400

    def test_requires_authentication(self, api_client, mother_user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = str(RefreshToken.for_user(mother_user))
        res = api_client.post(self.url, {"refresh": refresh})
        assert res.status_code == 401


@pytest.mark.django_db
class TestResendOTPView:
    url = "/api/auth/v1/resend-otp/"

    def test_returns_200_for_existing_email(self, api_client):
        MotherUserFactory(email="resend@example.com")
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            res = api_client.post(self.url, {"email": "resend@example.com"})
        assert res.status_code == 200

    def test_returns_200_for_nonexistent_email(self, api_client):
        # Should not leak whether email exists
        with patch("apps.accounts.tasks.send_otp_email.delay"):
            res = api_client.post(self.url, {"email": "ghost@example.com"})
        assert res.status_code == 200

    def test_returns_400_on_missing_email(self, api_client):
        res = api_client.post(self.url, {})
        assert res.status_code == 400


@pytest.mark.django_db
class TestCurrentUserView:
    url = "/api/auth/v1/whoami/"

    def test_returns_user_data(self, auth_client, mother_user):
        res = auth_client.get(self.url)
        assert res.status_code == 200
        assert res.data["email"] == mother_user.email

    def test_returns_profile_for_mother(self, auth_client, mother_user):
        res = auth_client.get(self.url)
        assert res.data["profile"] is not None

    def test_requires_authentication(self, api_client):
        res = api_client.get(self.url)
        assert res.status_code == 401


@pytest.mark.django_db
class TestUpdateUserProfileView:
    url = "/api/auth/v1/update/user/"

    def test_updates_username(self, auth_client):
        res = auth_client.patch(self.url, {"username": "newnick"})
        assert res.status_code == 200
        assert res.data["username"] == "newnick"

    def test_requires_authentication(self, api_client):
        res = api_client.patch(self.url, {"username": "x"})
        assert res.status_code == 401


@pytest.mark.django_db
class TestUpdateMotherProfileView:
    url = "/api/auth/v1/update/mother/"

    def test_updates_due_date(self, auth_client):
        res = auth_client.patch(self.url, {"baby_due_date": "2025-12-01"})
        assert res.status_code == 200

    def test_returns_404_for_partner(self, partner_auth_client):
        res = partner_auth_client.patch(self.url, {"baby_due_date": "2025-12-01"})
        assert res.status_code == 404

    def test_requires_authentication(self, api_client):
        res = api_client.patch(self.url, {"baby_due_date": "2025-12-01"})
        assert res.status_code == 401


@pytest.mark.django_db
class TestProfileImageView:
    url = "/api/auth/v1/profile/image/"

    def test_returns_400_when_no_file(self, auth_client):
        res = auth_client.put(self.url, {})
        assert res.status_code == 400

    def test_requires_authentication(self, api_client):
        res = api_client.put(self.url, {})
        assert res.status_code == 401

    def test_uploads_valid_image(self, auth_client):
        from django.core.files.uploadedfile import SimpleUploadedFile

        img = SimpleUploadedFile(
            "photo.jpg", b"fakeimagebytes", content_type="image/jpeg"
        )
        with patch(
            "cloudinary.uploader.upload",
            return_value={"public_id": "x", "secure_url": "https://img.com/x.jpg"},
        ):
            res = auth_client.put(self.url, {"profile_pic": img}, format="multipart")
        assert res.status_code == 200
        assert "url" in res.data
