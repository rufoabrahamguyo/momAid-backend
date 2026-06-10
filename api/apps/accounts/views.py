import logging

from core.throttles import LoginRateThrottle, OtpRateThrottle, UploadRateThrottle
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from . import services
from .serializers import (
    RegisterSerializer,
    ResendOTPSerializer,
    UpdateMotherProfileSerializer,
    UpdateUserProfileSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.register_user(**serializer.validated_data)
        return Response(
            {
                "detail": "Registration successful. Check your email for the activation code."
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, tokens = services.activate_user(**serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {"detail": "Account activated.", **tokens}, status=status.HTTP_200_OK
        )


class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OtpRateThrottle]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.resend_otp(email=serializer.validated_data["email"])
        return Response(
            {"detail": "If the email exists, a new code has been sent."},
            status=status.HTTP_200_OK,
        )


class LoginView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            services.logout_user(refresh_token=refresh_token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


# class GoogleLoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = GoogleLoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             _user, tokens, _created = services.google_login(**serializer.validated_data)
#         except ValueError as e:
#             return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
#         return Response(tokens, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateUserProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = services.update_user_profile(
            user=request.user,
            data=serializer.validated_data,
        )
        return Response(UserSerializer(user).data)


class UpdateMotherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateMotherProfileSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            services.update_mother_profile(
                user=request.user,
                data=serializer.validated_data,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Profile updated."})


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UploadRateThrottle]

    def put(self, request):
        file = request.FILES.get("profile_pic")
        if not file:
            return Response(
                {"detail": "Image file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            url = services.upload_profile_image(user=request.user, file=file)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Profile image updated.", "url": url})
