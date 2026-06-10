from django.urls import path

from .views import (
    ContinueWatchingView,
    CreateVideoCommentView,
    CreateVideoHistoryView,
    GetAllVideosView,
    ListVideoCommentsView,
    ListVideoHistoryView,
    ReplyCommentView,
    UploadUserVideoView,
    UserSpecificVideoView,
)

urlpatterns = [
    path("v1/upload/video/", UploadUserVideoView.as_view(), name="user-upload-video"),
    path(
        "v1/user/specific/videos/",
        UserSpecificVideoView.as_view(),
        name="user-specific-video",
    ),
    path("v1/videos/all/", GetAllVideosView.as_view(), name="get-all-videos"),
    path(
        "v1/videos/<int:video_id>/comments/",
        ListVideoCommentsView.as_view(),
        name="list-video-comments",
    ),
    path(
        "v1/videos/<int:video_id>/comments/create/",
        CreateVideoCommentView.as_view(),
        name="create-video-comment",
    ),
    path(
        "v1/comments/<int:comment_id>/reply/",
        ReplyCommentView.as_view(),
        name="reply-comment",
    ),
    path(
        "v1/history/create/<uuid:video_id>/",
        CreateVideoHistoryView.as_view(),
        name="video-history-create",
    ),
    path(
        "v1/history/continue/",
        ContinueWatchingView.as_view(),
        name="video-continue-watching",
    ),
    path("v1/history/list/", ListVideoHistoryView.as_view(), name="video-history-list"),
]
