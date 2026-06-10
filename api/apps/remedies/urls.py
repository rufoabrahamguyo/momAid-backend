"""Remedies routes."""

from django.urls import path

from apps.remedies import views

urlpatterns = [
    path(
        "conditions/", views.BabyConditionListView.as_view(), name="remedies-conditions"
    ),
]
