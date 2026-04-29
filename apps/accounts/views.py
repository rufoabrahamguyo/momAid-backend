import logging
import cloudinary.uploader
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from .helpers import generate_email_otp, verify_email_otp, verify_google_token

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save(is_active=False)
            email = user.email
            generate_email_otp(email)

            return Response(
                {"detail": "User created. Please activate your account."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ImageProfileUploader(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        MAX_SIZE = 10 * 1024 * 1024
        profile_pic = request.FILES.get("profile_pic")

        if not profile_pic:
            return Response({"detail": "No image provided"}, status=400)

        if profile_pic.size > MAX_SIZE:
            return Response({"detail": "Image must be <= 10MB"}, status=400)

        if not profile_pic.name.lower().endswith((".jpg", ".jpeg", ".png")):
            return Response({"detail": "Only jpg, jpeg, png allowed"}, status=400)

        user = request.user
        result = cloudinary.uploader.upload(
            profile_pic,
            public_id=f"user_{user.id}",
            overwrite=True
        )

        user.image = result["public_id"]
        user.save()

        return Response({
            "detail": "Profile image updated",
            "url": result["secure_url"]
        }, status=200)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        ser = UserSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({'detail': 'Refresh token required'}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (TokenError, InvalidToken) as e:
            return Response({'detail': str(e)}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user_otp = request.data.get("otp")

        if not email or not user_otp:
            return Response({"detail": "Email and OTP required"}, status=400)
        
        try:
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"detail": "User not found"}, status=404)

                verification_success = verify_email_otp(email, user_otp)

                if verification_success:
                    user.is_active = True
                    user.save()

                    refresh = RefreshToken.for_user(user)

                    return Response(
                        {
                            "detail": "Email verified successfully",
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                            "email": user.email,
                        },
                        status=200,
                    )

                return Response(
                    {"detail": "Invalid or expired OTP"},
                    status=400
                )

        except Exception as e:
            return Response({"detail": str(e)}, status=500)

        return Response({"detail": "Invalid or expired OTP"}, status=400)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_active:
            return Response({"detail": "You need to activate your account"}, status=403)
        return Response(UserSerializer(user).data, status=200)

class GoogleSocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        
        if not token:
            return Response({"detail": "Token is required"}, status=400)

        user_data = verify_google_token(token)
        if not user_data:
            return Response({"detail": "Invalid Google token"}, status=400)

        email = user_data.get("email")
        user, created = User.objects.get_or_create(email=email)
        
        user.is_active = True
        user.role = "mother"
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=200)