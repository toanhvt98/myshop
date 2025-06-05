from django.conf import settings
from datetime import timedelta

from backend.utils import string_to_timedelta


class EmailConfig:
    EMAIL_BACKEND = settings.EMAIL_BACKEND
    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_PORT = settings.EMAIL_PORT
    EMAIL_USE_TLS = settings.EMAIL_USE_TLS
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD

    def get_email_service_config(self):
        return {
            "backend": self.EMAIL_BACKEND,
            "host": self.EMAIL_HOST,
            "port": self.EMAIL_PORT,
            "use_tls": self.EMAIL_USE_TLS,
            "username": self.EMAIL_HOST_USER,
            "password": self.EMAIL_HOST_PASSWORD,
        }

class LanguageConfig:
    LANGUAGE_CODE = settings.LANGUAGE_CODE
    LANGUAGES = settings.LANGUAGES
    TIME_ZONE = settings.TIME_ZONE
    USE_I18N = settings.USE_I18N
    USE_L10N = settings.USE_L10N
    USE_TZ = settings.USE_TZ

    def get_language_config(self):
        return {
            "LANGUAGE_CODE": self.LANGUAGE_CODE,
            "LANGUAGES": self.LANGUAGES,
            "TIME_ZONE": self.TIME_ZONE,
            "USE_I18N": self.USE_I18N,
            "USE_L10N": self.USE_L10N,
            "USE_TZ": self.USE_TZ,
        }


class SiteConfig:
    SITE_NAME = settings.SITE_NAME
    MIN_LENGTH_PASSWORD= settings.MIN_LENGTH_PASSWORD
    FRONTEND_URL = settings.FRONTEND_URL
    RESET_PASSWORD_URL = settings.RESET_PASSWORD_URL
    COOKIE_DOMAIN = settings.COOKIE_DOMAIN
    COOKIE_HTTP_ONLY = settings.COOKIE_HTTP_ONLY
    COOKIE_SECURE = settings.COOKIE_SECURE
    COOKIE_SAME_SITE = settings.COOKIE_SAME_SITE
    COOKIE_PATH=settings.COOKIE_PATH
    def get_site_config(self):
        return {
            "SITE_NAME": self.SITE_NAME,
            'MIN_LENGTH_PASSWORD':self.MIN_LENGTH_PASSWORD,
            "FRONTEND_URL": self.FRONTEND_URL,
            "RESET_PASSWORD_URL": self.RESET_PASSWORD_URL,
            "COOKIE_DOMAIN": self.COOKIE_DOMAIN,
            "COOKIE_HTTP_ONLY": self.COOKIE_HTTP_ONLY,
            "COOKIE_SECURE": self.COOKIE_SECURE,
            "COOKIE_SAME_SITE": self.COOKIE_SAME_SITE,
            "COOKIE_PATH":self.COOKIE_PATH,
        }

class AuthConfig:
    LOCKING_ACCOUNT_ON_OTP_LIMIT = settings.LOCKING_ACCOUNT_ON_OTP_LIMIT
    MAX_OTP_ATTEMPTS_THRESHOLD = settings.MAX_OTP_ATTEMPTS_THRESHOLD
    OTP_ATTEMPT_WINDOW_LIFETIME = settings.OTP_ATTEMPT_WINDOW_LIFETIME
    LOCKING_ACCOUNT_LIFETIME = settings.LOCKING_ACCOUNT_LIFETIME

    OTP_LIMIT_EXCEEDED_ACTION = settings.OTP_LIMIT_EXCEEDED_ACTION

    MAX_TOTP_ATTEMPTS_THRESHOLD = settings.MAX_TOTP_ATTEMPTS_THRESHOLD
    TOTP_ATTEMPT_WINDOW_LIFETIME = settings.TOTP_ATTEMPT_WINDOW_LIFETIME

    OTP_EXPIRES_LIFETIME = settings.OTP_EXPIRES_LIFETIME
    OTP_RENEW_WINDOW_LIFETIME = settings.OTP_RENEW_WINDOW_LIFETIME
    OTP_LENGTH = settings.OTP_LENGTH
    TOTP_DIGITS = settings.TOTP_DIGITS
    OTP_MIXED_CASE = settings.OTP_MIXED_CASE

    def get_auth_config(self):
        return {
            "LOCKING_ACCOUNT_ON_OTP_LIMIT": self.LOCKING_ACCOUNT_ON_OTP_LIMIT,
            "OTP_LIMIT_EXCEEDED_ACTION": self.OTP_LIMIT_EXCEEDED_ACTION,
            "IS_DEACTIVATE" : self.OTP_LIMIT_EXCEEDED_ACTION == "DEACTIVATE",
            "MAX_OTP_ATTEMPTS_THRESHOLD": self.MAX_OTP_ATTEMPTS_THRESHOLD,
            "OTP_ATTEMPT_WINDOW_LIFETIME": int(string_to_timedelta(self.OTP_ATTEMPT_WINDOW_LIFETIME).total_seconds()),
            "LOCKING_ACCOUNT_LIFETIME": int(string_to_timedelta(self.LOCKING_ACCOUNT_LIFETIME).total_seconds()),


            "MAX_TOTP_ATTEMPTS_THRESHOLD": self.MAX_TOTP_ATTEMPTS_THRESHOLD,
            "TOTP_ATTEMPT_WINDOW_LIFETIME": int(string_to_timedelta(self.TOTP_ATTEMPT_WINDOW_LIFETIME).total_seconds()),

            'OTP_EXPIRES_LIFETIME': int(string_to_timedelta(self.OTP_EXPIRES_LIFETIME).total_seconds()),
            'OTP_RENEW_WINDOW_LIFETIME': int(string_to_timedelta(self.OTP_RENEW_WINDOW_LIFETIME).total_seconds()),
            'OTP_LENGTH': self.OTP_LENGTH,
            'TOTP_DIGITS':self.TOTP_DIGITS,
            'OTP_MIXED_CASE': self.OTP_MIXED_CASE,
        }

class SimpleJWTConfig:
    ENABLE_ROTATE_REFRESH_TOKEN = settings.ENABLE_ROTATE_REFRESH_TOKEN
    GET_NEW_REFRESH_TOKEN_WHILE_BELOW_IN = settings.GET_NEW_REFRESH_TOKEN_WHILE_BELOW_IN
    ACCESS_TOKEN_NAME = settings.ACCESS_TOKEN_NAME
    REFRESH_TOKEN_NAME = settings.REFRESH_TOKEN_NAME
    REFRESH_TOKEN_LIFETIME= settings.REFRESH_TOKEN_LIFETIME
    ACCESS_TOKEN_LIFETIME= settings.ACCESS_TOKEN_LIFETIME
    def get_simple_jwt_config(self):
        return {
            "ENABLE_ROTATE_REFRESH_TOKEN": self.ENABLE_ROTATE_REFRESH_TOKEN,
            "get_new_refresh_token_below_in_seconds": string_to_timedelta(self.GET_NEW_REFRESH_TOKEN_WHILE_BELOW_IN).total_seconds(),
            'ACCESS_TOKEN_NAME':self.ACCESS_TOKEN_NAME,
            'REFRESH_TOKEN_NAME':self.REFRESH_TOKEN_NAME,
            'access_token_lifetime_in_seconds':string_to_timedelta(self.ACCESS_TOKEN_LIFETIME).total_seconds(),
            'refresh_token_lifetime_in_seconds':string_to_timedelta(self.REFRESH_TOKEN_LIFETIME).total_seconds(),
        }