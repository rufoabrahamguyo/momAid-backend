from .base import *
import os
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


_db = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("POSTGRES_NAME"),
    "USER": os.getenv("POSTGRES_USER"),
    "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    "HOST": os.getenv("POSTGRES_HOST"),
    "PORT": os.getenv("POSTGRES_PORT", "5432"),
}
if env.bool("POSTGRES_SSL_REQUIRE", default=True):
    _db["OPTIONS"] = {"sslmode": "require"}

DATABASES = {"default": _db}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Source - https://stackoverflow.com/a/73013598
# Posted by diml
# Retrieved 2026-04-24, License - CC BY-SA 4.0

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL=EMAIL_HOST_USER
