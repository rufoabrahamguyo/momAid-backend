from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_NAME", "mumaid"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

CORS_ALLOW_ALL_ORIGINS = True

# Dev email: Mailpit (Compose sets EMAIL_HOST=mailpit) or local Mailpit on 1025; UI at http://localhost:8025
# Set EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend to log mail only.
if os.environ.get("EMAIL_BACKEND"):
    EMAIL_BACKEND = os.environ["EMAIL_BACKEND"]
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "127.0.0.1")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "1025"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() in ("true", "1", "yes")
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "MumAid <noreply@mumaid.local>")