from django.utils.translation import gettext_lazy as _

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
    TotpAuthenticationSerializer
)

from ..services import AuthenticationService

auth_config = AuthConfig().get_auth_config()
simplejwt_config = SimpleJWTConfig().get_simple_jwt_config()

class MeApiView(ProtectedBaseView):
    def get(self, request, *args, **kwargs):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data,status=200)

class LoginApiView(AuthBaseView):
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
        temp_auth_user = encrypt_data(data={'email':user_serializer.data.get('email'),'user_id':user_serializer.data.get('id')})
        max_age = auth_config['OTP_EXPIRES_LIFETIME']

        request._list_cookies = [
            set_cookies(
                key='auth_user_temp_info',
                value=temp_auth_user,
                max_age=max_age
            ),
        ]
        return Response({'enabled_2fa':enabled_2fa},status=200)


class VerifyLoginOtpApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        temp_auth_user = request.COOKIES.get('auth_user_temp_info')
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        temp_auth_user = decrypt_data(temp_auth_user)
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        email = temp_auth_user.get('email')
        user_id = temp_auth_user.get('user_id')
        if email is None or user_id is None:
            raise ValidationError(_('Cookie data is invalid.'))

        serializer_otp = OtpAuthenticationSerializer(data=data)
        serializer_otp.is_valid(raise_exception=True)
        user = AuthenticationService.verify_otp(email=email,**serializer_otp.validated_data)
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

class RequestLoginOtpApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        temp_auth_user = request.COOKIES.get('auth_user_temp_info')
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
                                          user_id=user_id)
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


class VerifyTotpLoginApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        temp_auth_user = request.COOKIES.get('auth_user_temp_info')
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        temp_auth_user = decrypt_data(temp_auth_user)
        if temp_auth_user is None:
            raise ValidationError(_('Required cookie is missing'))
        email = temp_auth_user.get('email')
        user_id = temp_auth_user.get('user_id')
        if email is None or user_id is None:
            raise ValidationError(_('Cookie data is invalid.'))
        serializer_otp = TotpAuthenticationSerializer(data=data)
        serializer_otp.is_valid(raise_exception=True)
        user = AuthenticationService.verify_totp(email=email,**serializer_otp.validated_data)
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
        return Response(user_serializer.data,status=200)




class LogoutApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(simplejwt_config['REFRESH_TOKEN_NAME'])
        if refresh_token is None:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as e:
                request._should_clean_auth_cookie = True
                return Response({'data':'success'},status=200)
        request._should_clean_auth_cookie = True
        return Response({'data':'success'},status=200)