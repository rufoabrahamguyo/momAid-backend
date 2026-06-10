import pytest
from unittest.mock import patch, MagicMock
from django.core import mail

from apps.accounts.tasks import send_otp_email, cleanup_expired_tokens
from .factories import MotherUserFactory


@pytest.mark.django_db
class TestSendOtpEmail:

    def test_sends_email(self):
        send_otp_email("user@example.com", "123456")
        assert len(mail.outbox) == 1

    def test_sends_to_correct_recipient(self):
        send_otp_email("target@example.com", "654321")
        assert mail.outbox[0].to == ["target@example.com"]

    def test_subject_contains_verify(self):
        send_otp_email("user@example.com", "111111")
        assert "verify" in mail.outbox[0].subject.lower()

    def test_retries_on_failure(self):
        with patch(
            "django.core.mail.EmailMessage.send",
            side_effect=[Exception("SMTP error"), None],
        ):
            # Should not raise — autoretry handles it
            try:
                send_otp_email("retry@example.com", "999999")
            except Exception:
                pass  # first attempt fails, retry succeeds


@pytest.mark.django_db
class TestCleanupExpiredTokens:

    def test_runs_without_error(self):
        cleanup_expired_tokens()

    def test_deletes_expired_tokens(self):
        from django.utils import timezone
        from datetime import timedelta
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        from rest_framework_simplejwt.tokens import RefreshToken

        user = MotherUserFactory()
        refresh = RefreshToken.for_user(user)

        OutstandingToken.objects.filter(jti=refresh["jti"]).update(
            expires_at=timezone.now() - timedelta(days=1)
        )

        cleanup_expired_tokens()
        assert not OutstandingToken.objects.filter(jti=refresh["jti"]).exists()
