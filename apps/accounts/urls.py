from django.urls import path
from .views import (
    RegisterView, 
    LogoutView, 
    VerifyTokenView, 
    CurrentUserView, 
    GoogleLoginView, 
    GoogleCallbackView,
    ImageProfileUploader
    )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("v1/register/", RegisterView.as_view(), name="register-user"),
    path("v1/login/", TokenObtainPairView.as_view(), name="login-user"),
    path("v1/login/refresh/token/", TokenRefreshView.as_view(), name="refresh-token"),
    path("v1/logout/", LogoutView.as_view(), name="logout-user"),
    path("v1/verify/token/", VerifyTokenView.as_view(), name="verify-otp-user"),
    path('v1/whoami/', CurrentUserView.as_view(),name="who-am-i"),
    path("v1/google/login/", GoogleLoginView.as_view(), name="google-login"),
    path("v1/google/callback/", GoogleCallbackView.as_view(), name="google-callback"),
    path("profile/image/", ImageProfileUploader.as_view(), name="profile-image"),
]
