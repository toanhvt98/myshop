from django.utils import translation
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from base.views import ProtectedBaseView, AuthBaseView
from base.utils import set_cookies, encrypt_data, decrypt_data
from base.config import SimpleJWTConfig, AuthConfig

from ..serializers.auth import (
    LoginSerializer,
    RegisterSerializer,
    EmailSerializer,
    ForgotPasswordSerializer, OtpLoginSerializer,
)

from ..serializers.model import (
    UserSerializer
)


from ..services import AuthenticationService,UserRegistrationService,UserForgotPasswordService

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
        serializer = LoginSerializer(data=data)
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

        is_enable_2fa_email = False
        for value in enabled_2fa:
            if value.get('type') == 'email':
                is_enable_2fa_email = True
                break

        if is_enable_2fa_email:
            AuthenticationService.generate_and_send_otp(email=user_serializer.data.get('email'),
                                              user_id=user_serializer.data.get('id'),
                                              current_language_code=user_serializer.data.get('language'))
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

        current_language_code = translation.get_language()
        serializer_otp = OtpLoginSerializer(data=data)
        serializer_otp.is_valid(raise_exception=True)
        user = AuthenticationService.verify_otp(email=email,current_language_code=current_language_code,**serializer_otp.validated_data)
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

class ResendLoginOtpApiView(AuthBaseView):
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
        current_language_code = translation.get_language()
        AuthenticationService.resend_otp(email=email,
                                          user_id=user_id,
                                          current_language_code=current_language_code)
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
        # need more action
        return Response({'data':'success'},status=200)

class RegisterApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data_copy = serializer.validated_data.copy()
        if 'password_confirmation' in validated_data_copy:
            validated_data_copy.pop('password_confirmation')
        user = UserRegistrationService.user_registration(**validated_data_copy)
        user_serializer = UserSerializer(user)
        refresh_token = RefreshToken.for_user(user)
        request._new_access_token = str(refresh_token.access_token)
        request._new_refresh_token = str(refresh_token)
        return Response(user_serializer.data,status=201)

# forgot password step 1
class ForgotPasswordStepOneApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        current_language_code = translation.get_language()
        data = request.data
        serializer = ForgotPasswordSerializer(data=data,context={'fields':['email']})
        serializer.is_valid(raise_exception=True)
        user = UserForgotPasswordService.validate_user_email(**serializer.validated_data)
        UserForgotPasswordService.create_email_otp_forgot_password(current_language_code=current_language_code,user_id=user.pk,**serializer.validated_data)
        user_2fa_enabled = UserForgotPasswordService.get_list_user_2fa_enabled(user)
        return Response({'data':user_2fa_enabled},status=200)

# forgot password step 2
class ForgotPasswordStepTwoApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data,context={'fields':['type']})
        serializer.is_valid(raise_exception=True)
        return Response({'data':'success'},status=200)
