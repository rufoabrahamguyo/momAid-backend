from django.urls import path
from .views import welcome_view

urlpatterns = [
    path('health/', welcome_view, name='api-health-check')
]
