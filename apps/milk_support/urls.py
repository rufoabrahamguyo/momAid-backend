"""Milk support routes."""

from django.urls import path

from apps.milk_support import views

urlpatterns = [
    path("listings/", views.MilkListingListCreateView.as_view(), name="milk-listings"),
    path("listings/<int:pk>/", views.MilkListingRetrieveDestroyView.as_view(), name="milk-listing-detail"),
]
