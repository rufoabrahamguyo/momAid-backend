"""Healthcare routes."""

from django.urls import path

from apps.healthcare import views

urlpatterns = [
    path("emergency-contacts/", views.EmergencyContactListCreateView.as_view(), name="emergency-contacts"),
    path(
        "emergency-contacts/<int:pk>/",
        views.EmergencyContactDetailView.as_view(),
        name="emergency-contact-detail",
    ),
    path("hospitals/nearby/", views.HospitalNearbyView.as_view(), name="hospitals-nearby"),
    path("emergency/", views.EmergencyTriggerView.as_view(), name="healthcare-emergency"),
]
