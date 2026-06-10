from django.apps import AppConfig


class WelcomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.welcome"
    label = "welcome"
    verbose_name = "Welcome"
