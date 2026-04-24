"""Settings for `manage.py test` without Docker (SQLite in memory)."""

import os

os.environ.setdefault("SECRET_KEY", "django-insecure-test-only-not-for-production")

from .base import *  # noqa: E402

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_USE_CELERY = False

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
