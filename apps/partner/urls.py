"""Partner routes."""

from django.urls import path

from apps.partner import views

urlpatterns = [
    path("connect/", views.PartnerConnectView.as_view(), name="partner-connect"),
    path("tasks/", views.PartnerTaskListView.as_view(), name="partner-tasks"),
    path("tasks/<int:pk>/complete/", views.PartnerTaskCompleteView.as_view(), name="partner-task-complete"),
    path("completions/", views.PartnerCompletionListView.as_view(), name="partner-completions"),
]
