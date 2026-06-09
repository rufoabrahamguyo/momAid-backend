from django.urls import path

from .views import (
    MumTalkPostCreateView, 
    MumTalkPostListView, 
    MumTalkPostDetailView, 
    MumTalkPostDeleteView, 
    MumTalkListUserPostsView,
    MumTalkPostUpdateView,
    MumTalkReplyCreateView,
)


urlpatterns = [
    path("v1/posts/", MumTalkPostListView.as_view(), name="mumtalk-post-list"),
    path("v1/posts/create/", MumTalkPostCreateView.as_view(), name="mumtalk-post-create"),
    path("v1/posts/<str:post_id>/", MumTalkPostDetailView.as_view(), name="mumtalk-post-detail"),
    path("v1/posts/<str:post_id>/delete/", MumTalkPostDeleteView.as_view(), name="mumtalk-post-delete"),
    path("v1/posts/me/", MumTalkListUserPostsView.as_view(), name="mumtalk-user-posts"),
    path("v1/posts/<str:post_id>/update/", MumTalkPostUpdateView.as_view(), name="mumtalk-post-update"),
    path("v1/posts/<str:post_id>/replies/create/", MumTalkReplyCreateView.as_view(), name="mumtalk-reply-create"),
]

