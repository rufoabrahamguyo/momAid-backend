from .base import *

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

# Security (production only)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True