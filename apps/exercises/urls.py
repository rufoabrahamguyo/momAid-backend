"""Exercises routes."""

from django.urls import path

from apps.exercises import views

urlpatterns = [
    path("", views.ExerciseListView.as_view(), name="exercise-list"),
]
