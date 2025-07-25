from typing import Any, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from djoser.views import TokenCreateView
from loguru import logger
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .emails import send_otp_email
from .utils import generate_otp
from django.contrib.auth.hashers import make_password, check_password


User = get_user_model()


def set_auth_cookies(
    response: Response, access_token: str, refresh_token: Optional[str] = None
) -> None:
    access_token_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
    cookie_settings = {
        "path": settings.COOKIE_PATH,
        "secure": settings.COOKIE_SECURE,
        "httponly": settings.COOKIE_HTTPONLY,
        "samesite": settings.COOKIE_SAMESITE,
        "max_age": access_token_lifetime,
    }
    response.set_cookie("access", access_token, **cookie_settings)

    if refresh_token:
        refresh_token_lifetime = settings.SIMPLE_JWT[
            "REFRESH_TOKEN_LIFETIME"
        ].total_seconds()
        refresh_cookie_settings = cookie_settings.copy()
        refresh_cookie_settings["max_age"] = refresh_token_lifetime
        response.set_cookie("refresh", refresh_token, **refresh_cookie_settings)

    logged_in_cookie_settings = cookie_settings.copy()
    logged_in_cookie_settings["httponly"] = False
    response.set_cookie("logged_in", "true", **logged_in_cookie_settings)


class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        user = serializer.user
        user.maybe_unlock_account()
        if user.is_locked_out():
            return Response(
                {
                    "error": f"Account is locked due to multiple failed login attempts."
                    f"Please try again after {settings.LOCKOUT_DURATION.total_seconds() / 60} minutes"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        user.reset_failed_login_attempts()

        otp = generate_otp()
        user.set_otp(otp)
        send_otp_email(user.email, otp)

        logger.info(f"OTP sent for login to user: {user.email}")
        return Response(
            {
                "success": "OTP sent to your email",
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            return self._action(serializer)

        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            user.maybe_unlock_account()
            user.handle_failed_login_attempts()
            failed_attempts = user.failed_login_attempt
            logger.error(f"Failed login attempts: {failed_attempts} for user: {email}")

            if failed_attempts >= settings.LOGIN_ATTEMPTS:
                return Response(
                    {
                        "error": (
                            "You have exceeded the maximum number of login attempts. "
                            "Your account has been locked for "
                            f"{settings.LOCKOUT_DURATION.total_seconds() / 60} minutes."
                            "An email has been sent to you with further instructions."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(
            {"error": "Your login credentials are not correct"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        refresh_token = request.COOKIES.get("refresh")

        if refresh_token:
            data = request.data.copy()
            data["refresh"] = refresh_token
            request._full_data = data

        refresh_res = super().post(request, *args, **kwargs)

        if refresh_res.status_code == status.HTTP_200_OK:
            access_token = refresh_res.data.get("access")
            refresh_token = refresh_res.data.get("refresh")

            if access_token and refresh_token:
                set_auth_cookies(
                    refresh_res,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )
                refresh_res.data.pop("access", None)
                refresh_res.data.pop("refresh", None)

                refresh_res.data["message"] = "Access tokens refreshed successfully."

            else:
                refresh_res.data["message"] = (
                    'Access or refresh token not found in refresh " "response data'
                )
                logger.error(
                    "Access or refresh token not found in refresh response data"
                )

        return refresh_res


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp = request.data.get("otp")

        if not otp:
            return Response(
                {"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Received OTP: {otp}")

        # Find users with non-expired OTPs
        now = timezone.now()
        users = User.objects.filter(otp_expiry_time__gt=now)

        user = None
        for u in users:
            if check_password(otp, u.otp):
                user = u
                break

        if not user:
            logger.info("No user found with provided OTP")
            return Response(
                {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check account lock status
        user.maybe_unlock_account()
        if user.is_locked_out():
            return Response(
                {
                    "error": f"Account is locked due to multiple failed login attempts. "
                    f"Please try again after {settings.LOCKOUT_DURATION.total_seconds() / 60} minutes"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Mark OTP as used
        user.otp = ""
        user.otp_expiry_time = None
        user.save()

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "success": "Login successful. Now add your profile information, so that we can create an account for you."
            },
            status=status.HTTP_200_OK,
        )
        set_auth_cookies(response, access_token, refresh_token)
        logger.info(f"Successful login with OTP: {user.email}")
        return response


class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        response.delete_cookie("logged_in")
        return response
