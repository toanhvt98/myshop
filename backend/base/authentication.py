from .config import SimpleJWTConfig
from .utils import set_cookies
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
import time
import logging

logger = logging.getLogger(__name__)
simplejwt_config = SimpleJWTConfig().get_simple_jwt_config()

class AuthenticationMixin(JWTAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get(simplejwt_config['ACCESS_TOKEN_NAME'])
        refresh_token = request.COOKIES.get(simplejwt_config['REFRESH_TOKEN_NAME'])
        new_access_token = None
        new_refresh_token=None
        validation_token =None
        request._should_clean_auth_cookie = True

        if not refresh_token or refresh_token is None:
            raise AuthenticationFailed(_('Token is missing.'))

        try:
            if not access_token:
                raise InvalidToken()
            validation_token = self.get_validated_token(access_token)
        except InvalidToken:
            try:
                refresh = RefreshToken(refresh_token)
                if simplejwt_config['ENABLE_ROTATE_REFRESH_TOKEN']:
                    decoded_payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=settings.SIMPLE_JWT['ALGORITHM'])
                    exp = int(decoded_payload['exp'])
                    time_now = int(time.time())
                    time_to_re_new = simplejwt_config['get_new_refresh_token_below_in_seconds']
                    if time_now + time_to_re_new > exp:
                        refresh.blacklist()
                        refresh.set_jti()
                        refresh.set_iat()
                        refresh.set_exp()
                new_refresh_token = str(refresh)
                new_access_token = str(refresh.access_token)
            except (TokenError,InvalidToken) as e:
                return None
        if validation_token:
            try:
                user = self.get_user(validation_token)
                request._should_clean_auth_cookie = False
                return user, validation_token
            except Exception as e:
                logger.error(f"An error occurred while authenticating user in 'validation_token': {e}")
                raise AuthenticationFailed(
                    _("An error occurred while authenticating your request. Please try again later or contact support."))

        if new_access_token and new_refresh_token:
            try:
                validation_token = self.get_validated_token(new_access_token)
                user = self.get_user(validation_token)
                request._should_clean_auth_cookie = False
                request._list_cookies = [
                set_cookies(
                    key=simplejwt_config['REFRESH_TOKEN_NAME'],
                    value=new_refresh_token,
                    max_age=simplejwt_config['refresh_token_lifetime_in_seconds']),
                set_cookies(
                    key=simplejwt_config['ACCESS_TOKEN_NAME'],
                    value=new_access_token,
                    max_age=simplejwt_config['access_token_lifetime_in_seconds']),
            ]
                return user, validation_token
            except Exception as e:
                logger.error(f"An error occurred while authenticating user in 'new_access_token' and 'new_refresh_token': {e}")
                raise AuthenticationFailed(
                    _("An error occurred while authenticating your request. Please try again later or contact support."))
        raise AuthenticationFailed(_('Invalid token.'))


