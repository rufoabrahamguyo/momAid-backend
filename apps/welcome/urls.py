from django.urls import path
from .views import welcome_view

urlpatterns = [
    path('/', welcome_view.as_view(), name='api-health-check') 
]
