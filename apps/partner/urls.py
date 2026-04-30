from django.urls import path
from .views import (
    GenerateCodeView,
    LinkPartnerView,
    CreatePartnerTaskCompletionView,
    CreatePartnerTaskView,
    ListPartnerTaskView,
    ListPartnerTaskCompletion,
)

urlpatterns = [
    path("v1/generate/code/", GenerateCodeView.as_view(), name="generate-code"),
    path("v1/link/partner/", LinkPartnerView.as_view(), name="link-partner"),
    path("v1/create/partner/tasks/", CreatePartnerTaskView.as_view(), name="create-partner-tasks"),
    path("v1/list/partner/tasks/", ListPartnerTaskView.as_view(), name="list-partner-tasks"),
    path("v1/list/completion/tasks/", ListPartnerTaskCompletion.as_view(), name="list-completed-tasks"),
    path("v1/<int:task_id>/complete/", CreatePartnerTaskCompletionView.as_view(), name="create-partner-task"),

]
