import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework.test import APIClient

User = get_user_model()


def _tiny_png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1, 1), color=(200, 100, 50)).save(buf, format="PNG")
    return buf.getvalue()


class ProfileAPITest(TestCase):
    def setUp(self):
        self._media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self._media, ignore_errors=True)
        self.mother = User.objects.create_user(
            email="mother@test.example",
            password="secret",
            role=User.Role.MOTHER,
        )

    def _client(self) -> APIClient:
        c = APIClient()
        c.force_authenticate(user=self.mother)
        return c

    def test_get_profile_includes_null_avatar(self):
        c = self._client()
        with self.settings(MEDIA_ROOT=self._media):
            r = c.get("/api/auth/v1/profile/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("avatar", r.data)
        self.assertIsNone(r.data["avatar"])

    def test_patch_multipart_avatar_returns_absolute_url(self):
        c = self._client()
        img = SimpleUploadedFile(
            "a.png",
            _tiny_png_bytes(),
            content_type="image/png",
        )
        with self.settings(MEDIA_ROOT=self._media):
            r = c.patch(
                "/api/auth/v1/profile/",
                {"avatar": img},
                format="multipart",
            )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIsNotNone(r.data.get("avatar"))
        self.assertTrue(
            r.data["avatar"].startswith("http://testserver/media/avatars/"),
        )

    def test_patch_json_clears_avatar(self):
        c = self._client()
        img = SimpleUploadedFile(
            "a.png",
            _tiny_png_bytes(),
            content_type="image/png",
        )
        with self.settings(MEDIA_ROOT=self._media):
            c.patch(
                "/api/auth/v1/profile/",
                {"avatar": img},
                format="multipart",
            )
            r = c.patch(
                "/api/auth/v1/profile/",
                {"avatar": None},
                format="json",
            )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIsNone(r.data.get("avatar"))
