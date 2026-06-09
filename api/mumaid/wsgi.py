"""WSGI config for MumAid."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mumaid.settings")

application = get_wsgi_application()
