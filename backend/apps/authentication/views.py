from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.contrib.auth import get_user_model
import logging

from apps.authentication.models import EmailVerificationToken
from apps.authentication.services.email_service import EmailService
from apps.authentication.serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserMeSerializer
)

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        email_sent = False
        if settings.EMAIL_VERIFICATION_REQUIRED:
            token = EmailVerificationToken.generate_token(
                user,
                expires_in_hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS,
            )
            try:
                EmailService.send_verification_email(user, token)
                email_sent = True
            except Exception:
                logger.exception("Failed to send verification email to %s", user.email)
        else:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])

        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "is_email_verified": user.is_email_verified,
                "email_sent": email_sent,
                "verification_expiry_hours": settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS,
                "message": (
                    "Registration successful. Please check your email to verify your account."
                    if settings.EMAIL_VERIFICATION_REQUIRED
                    else "Registration successful."
                ),
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token_str = request.query_params.get('token')
        if not token_str:
            return Response(
                {"error": {"code": "missing_token", "message": "Verification token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = EmailVerificationToken.objects.select_related('user').get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": {"code": "invalid_token", "message": "Invalid verification token."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if token.is_verified:
            return Response(
                {"error": {"code": "already_verified", "message": "Email is already verified."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if token.is_expired():
            return Response(
                {"error": {"code": "expired_token", "message": "Verification token has expired."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token.user.is_email_verified = True
        token.user.save(update_fields=['is_email_verified'])
        token.is_verified = True
        token.save(update_fields=['is_verified'])
        return Response({"message": "Email verified successfully.", "email": token.user.email})


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        generic_message = "If the email exists, a verification link has been sent."
        if not email:
            return Response(
                {"error": {"code": "missing_email", "message": "Email is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = get_user_model().objects.get(email__iexact=email)
        except get_user_model().DoesNotExist:
            return Response({"message": generic_message})

        if user.is_email_verified:
            return Response({"message": generic_message})

        token = EmailVerificationToken.generate_token(
            user,
            expires_in_hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS,
        )
        try:
            EmailService.send_verification_email(user, token)
        except Exception:
            logger.exception("Failed to resend verification email to %s", user.email)
            return Response(
                {"error": {"code": "email_failed", "message": "Failed to send verification email."}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"message": generic_message})
