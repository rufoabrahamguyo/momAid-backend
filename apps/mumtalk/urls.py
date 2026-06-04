from django.urls import path

from .views import MumTalkPostCreateView, MumTalkPostListView


urlpatterns = [
    path("v1/posts/", MumTalkPostListView.as_view(), name="mumtalk-post-list"),
    path("v1/posts/create/", MumTalkPostCreateView.as_view(), name="mumtalk-post-create"),
]
