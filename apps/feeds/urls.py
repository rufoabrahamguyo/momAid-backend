from django.urls import path
from .views import UploadUserVideoView, GetAllVideosView, UserSpecificVideoView

urlpatterns = [
    path("v1/upload/video/", UploadUserVideoView.as_view(), name='user-upload-video'),
    path("v1/user/specific/videos", UserSpecificVideoView.as_view(), name="user-specific-video"),
    path("v1/videos/all/", GetAllVideosView.as_view(), name="get-all-videos")
]