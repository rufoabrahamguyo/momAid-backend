from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]


CORS_ALLOW_ALL_ORIGINS = True

EMAIL_USE_CELERY = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "mailpit"
EMAIL_PORT = 1025

EMAIL_HOST_USER = ""        
EMAIL_HOST_PASSWORD = ""   

EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = "noreply@mumaid.local"

