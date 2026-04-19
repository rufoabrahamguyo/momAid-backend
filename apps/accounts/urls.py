"""URL routes for authentication."""

from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("verify-otp/", views.VerifyOTPView.as_view(), name="auth-verify-otp"),
    path("logout/", views.LogoutAPIView.as_view(), name="auth-logout"),
    path("user/", views.UserProfileView.as_view(), name="auth-user"),
]
