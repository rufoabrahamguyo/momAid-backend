from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]

MIDDLEWARE = [
    m
    for m in MIDDLEWARE
    if m
    not in [
        "core.middleware.GlobalRateLimiter",
    ]
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test_db",
    }
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


MIGRATION_MODULES = {}

REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": None,
        "user": None,
        "otp_limit": None,
        "login_limit": None,
        "auth_limit": None,
        "upload_limit": None,
    },
}
