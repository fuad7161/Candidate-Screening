from django.urls import path
from apps.authentication.views import (
    RegisterView,
    LoginView,
    CustomTokenRefreshView,
    UserMeView,
    VerifyEmailView,
    ResendVerificationEmailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', UserMeView.as_view(), name='auth-me'),
    path('verify-email/', VerifyEmailView.as_view(), name='auth-verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='auth-resend-verification'),
]
