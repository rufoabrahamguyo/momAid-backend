from pathlib import Path
import os
import environ
from datetime import timedelta
import cloudinary

# Adjusted to point to project root from settings/base.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
# Only read .env here if it exists, otherwise environment variables handle it
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))



SECRET_KEY = env("SECRET_KEY", default="django-insecure-default-key-change-me")

INSTALLED_APPS = [
    "cloudinary_storage",
    "django.contrib.staticfiles",
    "cloudinary",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "anymail",
    "apps.accounts",
    "apps.opportunities",
    "apps.remedies",
    "apps.exercises",
    "apps.milk_support",
    "apps.partner",
    "apps.healthcare",
    "apps.notifications",
    "apps.feeds",
    "apps.mumtalk",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
"mumaid.middleware.error_middleware.ErrorHandlerMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.accounts.middleware.MomAidGlobalRateLimiter",
]

ROOT_URLCONF = "mumaid.urls"
WSGI_APPLICATION = "mumaid.wsgi.application"

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '2/minute',
        'user': '1000/day',

        'otp_limit': '3/minute',
        'login_limit': '5/minute',
        'auth_limit': '40/day',
        'upload_limit': '5/day',
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": SECRET_KEY,
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'},
    },
    'handlers': {
        'console': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'verbose'},
    },
    'loggers': {
        '': {'handlers': ['console'], 'level': 'INFO'},
    },
}

CELERY_BEAT_SCHEDULE = {
    'daily-db-cleanup': {
        'task': 'apps.accounts.tasks.cleanup_stale_data',
        'schedule': 86400.0, 
    },
}


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'   

import cloudinary

cloudinary.config(
    cloud_name=env("CLOUDINARY_CLOUD_NAME"),
    api_key=env("CLOUDINARY_CLOUD_API_KEY"),
    api_secret=env("CLOUDINARY_CLOUD_API_SECRET"),
    secure=True
)


