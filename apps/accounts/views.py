import logging
import cloudinary.uploader
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle

from .serializers import RegisterSerializer, UserSerializer,UpdateMotherProfileSerializer,UpdateUserProfileSerializer
from .helpers import generate_email_otp, verify_email_otp, verify_google_token, resend_otp
from .throttle import CustomRegistrationThrottle
from mumaid.utils.discord import send_error_to_discord

User = get_user_model()
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            with transaction.atomic():
                serializer = RegisterSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save(is_active=False)
                generate_email_otp(user.email)

                return Response(
                    {"detail": "Registration successful. Please check your email for the activation code."},
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            logger.error(f"Reg_Error: {str(e)}")
            return Response(
                {"detail": "An error occurred during registration."},
                status=status.HTTP_400_BAD_REQUEST
            )

class ImageProfileUploaderView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        MAX_SIZE = 5 * 1024 * 1024
        profile_pic = request.FILES.get("profile_pic")

        if not profile_pic:
            return Response({"detail": "Image file is required."}, status=status.HTTP_400_BAD_REQUEST)

        if profile_pic.size > MAX_SIZE:
            return Response({"detail": "File size exceeds 5MB limit."}, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = ["image/jpeg", "image/png", "image/jpg"]
        if profile_pic.content_type not in allowed_types:
            return Response({"detail": "Unsupported file type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.user
            result = cloudinary.uploader.upload(
                profile_pic,
                folder="profile_pics/",
                public_id=f"user_{user.id}",
                overwrite=True,
                resource_type="image"
            )
            user.image = result.get("public_id")
            user.save()
            return Response({"detail": "Profile updated.", "url": result.get("secure_url")}, status=200)
        except Exception as e:
            logger.error(f"Upload_Error: {str(e)}")

            send_error_to_discord({
                "Alert": "❌ Upload Key Failure",
                "Message": f"Invalid API Key attempted",
                "Exception": str(e)
            })

            return Response({"detail": "Failed to upload image."}, status=500)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Token required."}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid token."}, status=400)
        except Exception as e:
            logger.error(f"Logout_Error: {str(e)}")
            return Response({"detail": "Logout failed."}, status=500)

class VerifyTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"detail": "Credentials required."}, status=400)
        
        try:
            user = User.objects.filter(email=email).first()
            if user and verify_email_otp(email, otp):
                user.is_active = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "detail": "Account activated.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                }, status=200)
            
            return Response({"detail": "Invalid email or code."}, status=401)
        except Exception as e:
            logger.error(f"Verify_Error: {str(e)}")
            return Response({"detail": "Verification failed."}, status=500)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_active:
            return Response({"detail": "Account inactive."}, status=403)

        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=200)

class GoogleSocialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "Token required."}, status=400)

        user_data = verify_google_token(token)
        if not user_data:
            return Response({"detail": "Authentication failed."}, status=401)

        email = user_data.get("email")
        with transaction.atomic():
            user, created = User.objects.get_or_create(email=email)
            user.is_active = True
            if created:
                user.role = "mother"
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=200)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({'detail': 'Email required.'}, status=400)

        try:
            if User.objects.filter(email=email).exists():
                resend_otp(email)
            return Response({'detail': 'If the email exists, a code has been sent.'}, status=200)
        except Exception as e:
            logger.error(f"Resend_Error: {str(e)}")
            return Response({'detail': 'Failed to process request.'}, status=500)

class UpdateUserProfileView(APIView):

    def put(self, request):
        serializer = UpdateUserProfileSerializer(instance=request.user, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'detail': 'User Profile updated successfully'
            }, status=200)

class UpdateMotherProfileView(APIView):

    def put(self, request):

        profile = getattr(request.user, 'mother_profile', None)

        if not profile:
            return Response({'error': 'Mother profile not found'}, status=404)
            
        serializer = UpdateMotherProfileSerializer(instance=profile, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'detail': 'User Profile updated successfully'
            },status=200)

