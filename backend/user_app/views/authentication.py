import datetime

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from base.views import ProtectedBaseView, AuthBaseView
from base.utils import set_cookies, encrypt_data, decrypt_data
from base.config import SimpleJWTConfig, AuthConfig

from ..serializers import (
    UserSerializer,
    AuthenticationSerializer,
    OtpAuthenticationSerializer,
)

from ..services import AuthenticationService

auth_config = AuthConfig().get_auth_config()
simplejwt_config = SimpleJWTConfig().get_simple_jwt_config()

class MeApiView(ProtectedBaseView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data,status=200)

class SignInApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = AuthenticationSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = AuthenticationService.authenticate_with_password(**serializer.validated_data)
        user_serializer = UserSerializer(user)
        enabled_2fa = user_serializer.data.get('enabled_2fa')
        if len(enabled_2fa) == 0:
            refresh_token = RefreshToken.for_user(user)
            request._list_cookies = [
                set_cookies(
                    key=simplejwt_config['REFRESH_TOKEN_NAME'],
                    value=str(refresh_token),
                    max_age=simplejwt_config['refresh_token_lifetime_in_seconds']
                ),
                set_cookies(
                    key=simplejwt_config['ACCESS_TOKEN_NAME'],
                    value=str(refresh_token.access_token),
                    max_age=simplejwt_config['access_token_lifetime_in_seconds']
                ),
            ]
            return Response(user_serializer.data,status=200)
        max_age = auth_config['OTP_EXPIRES_LIFETIME']
        expires_at = timezone.now() + datetime.timedelta(seconds=max_age)
        temp_auth_user = encrypt_data(
            data={'email': user_serializer.data.get('email'),
                  'user_id': user_serializer.data.get('id'),
                  'expires_at': expires_at.timestamp() ,
                  }
        )
        request._list_cookies = [
            set_cookies(
                key='auth_user_temp_info',
                value=temp_auth_user,
                max_age=max_age
            ),
        ]
        return Response({'enabled_2fa':enabled_2fa},status=200)


class VerifySignInOtpApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        temp_auth_user = request.COOKIES.get('auth_user_temp_info')
        language_code = translation.get_language()
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        temp_auth_user = decrypt_data(temp_auth_user)
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        email = temp_auth_user.get('email')
        user_id = temp_auth_user.get('user_id')
        expires_at = temp_auth_user.get('expires_at')
        if email is None or user_id is None or expires_at is None or not isinstance(expires_at,float):
            raise ValidationError(_('Cookie data is invalid.'))
        if timezone.now().timestamp() > expires_at:
            raise ValidationError(_('Cookie data has expired. Please request a new one.'))
        serializer_otp = OtpAuthenticationSerializer(data=data)
        serializer_otp.is_valid(raise_exception=True)
        otp_type = serializer_otp.validated_data.get('otp_type')
        serializer_otp.validated_data.pop('otp_type')
        if otp_type == 'email':
            user = AuthenticationService.verify_otp(email=email,language_code=language_code,**serializer_otp.validated_data)
        elif otp_type == 'totp':
            user = AuthenticationService.verify_totp(email=email,language_code=language_code,**serializer_otp.validated_data)
        else:
            raise ValidationError(_('Please enter a valid type.'))
        user_serializer = UserSerializer(user)
        refresh_token = RefreshToken.for_user(user)
        request._list_cookies = [
            set_cookies(
                key=simplejwt_config['REFRESH_TOKEN_NAME'],
                value=str(refresh_token),
                max_age=simplejwt_config['refresh_token_lifetime_in_seconds']
            ),
            set_cookies(
                key=simplejwt_config['ACCESS_TOKEN_NAME'],
                value=str(refresh_token.access_token),
                max_age=simplejwt_config['access_token_lifetime_in_seconds']
            ),
        ]
        request._list_key_deleting_cookies = ['auth_user_temp_info']
        return Response(user_serializer.data, status=200)


class RequestSignInOtpApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        temp_auth_user = request.COOKIES.get('auth_user_temp_info')
        language_code = translation.get_language()
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        temp_auth_user = decrypt_data(temp_auth_user)
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        email = temp_auth_user.get('email')
        user_id = temp_auth_user.get('user_id')
        if email is None or user_id is None:
            raise ValidationError(_('Cookie data is invalid.'))
        AuthenticationService.generate_and_send_otp(email=email,
                                          user_id=user_id,language_code=language_code
                                                    )
        auth_user_temp_info = request.COOKIES.get('auth_user_temp_info')
        max_age = auth_config['OTP_EXPIRES_LIFETIME']
        request._list_cookies = [
            set_cookies(
                key='auth_user_temp_info',
                value=auth_user_temp_info,
                max_age=max_age
            ),
        ]
        return Response({'data':'success'},status=200)

class SignOutApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(simplejwt_config['REFRESH_TOKEN_NAME'])
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        except Exception as e:
            request._should_clean_auth_cookie = True
            return Response({'data':'success'},status=200)
        request._should_clean_auth_cookie = True
        return Response({'data': 'success'}, status=200)