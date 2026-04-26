from django.urls import path
from .views import (
    UploadUserVideoView,
    GetAllVideosView, 
    UserSpecificVideoView,
    ListVideoCommentsView,
    CreateVideoCommentView,
    ReplyCommentView
)

urlpatterns = [
    path("v1/upload/video/", UploadUserVideoView.as_view(), name='user-upload-video'),
    path("v1/user/specific/videos/", UserSpecificVideoView.as_view(), name="user-specific-video"),
    path("v1/videos/all/", GetAllVideosView.as_view(), name="get-all-videos"),
    path("v1/videos/<int:video_id>/comments/",ListVideoCommentsView.as_view(),name="list-video-comments"),
    path("v1/videos/<int:video_id>/comments/create/",CreateVideoCommentView.as_view(),name="create-video-comment"),
    path("v1/comments/<int:comment_id>/reply/",ReplyCommentView.as_view(),name="reply-comment"),
]