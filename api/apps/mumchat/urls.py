from django.urls import path

from .views import (
    MumChatListUserPostsView,
    MumChatPostCreateView,
    MumChatPostDeleteView,
    MumChatPostDetailView,
    MumChatPostListView,
    MumChatPostUpdateView,
    MumChatReplyCreateView,
)

urlpatterns = [
    path("v1/posts/", MumChatPostListView.as_view(), name="mumchat-post-list"),
    path(
        "v1/posts/create/", MumChatPostCreateView.as_view(), name="mumchat-post-create"
    ),
    path("v1/posts/me/", MumChatListUserPostsView.as_view(), name="mumchat-user-posts"),
    path(
        "v1/posts/<str:post_id>/",
        MumChatPostDetailView.as_view(),
        name="mumchat-post-detail",
    ),
    path(
        "v1/posts/<str:post_id>/delete/",
        MumChatPostDeleteView.as_view(),
        name="mumchat-post-delete",
    ),
    path(
        "v1/posts/<str:post_id>/update/",
        MumChatPostUpdateView.as_view(),
        name="mumchat-post-update",
    ),
    path(
        "v1/posts/<str:post_id>/replies/create/",
        MumChatReplyCreateView.as_view(),
        name="mumchat-reply-create",
    ),
]
