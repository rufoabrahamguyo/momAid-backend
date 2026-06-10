from django.urls import path
from .views import (
    RegisterView,
    LogoutView,
    VerifyOTPView,
    CurrentUserView,
    ProfileImageView,
    # GoogleSocialLoginView,
    ResendOTPView,
    UpdateMotherProfileView,
    UpdateUserProfileView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.throttling import ScopedRateThrottle


class ThrottledCustomTokenPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login_limit"


urlpatterns = [
    path("v1/register/", RegisterView.as_view(), name="register-user"),
    path("v1/login/", ThrottledCustomTokenPairView.as_view(), name="login-user"),
    path("v1/login/refresh/token/", TokenRefreshView.as_view(), name="refresh-token"),
    path("v1/logout/", LogoutView.as_view(), name="logout-user"),
    path("v1/verify/token/", VerifyOTPView.as_view(), name="verify-otp-user"),
    path("v1/resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("v1/whoami/", CurrentUserView.as_view(), name="who-am-i"),
    # path("v1/google/social-login/", GoogleSocialLoginView.as_view(), name="google-social-login"),
    path("v1/profile/image/", ProfileImageView.as_view(), name="profile-image"),
    path(
        "v1/update/user/", UpdateUserProfileView.as_view(), name="update-user-profile"
    ),
    path(
        "v1/update/mother/",
        UpdateMotherProfileView.as_view(),
        name="update-mother-profile",
    ),
]
