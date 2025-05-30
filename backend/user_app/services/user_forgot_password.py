import json
import logging

from cryptography.fernet import Fernet
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_redis import get_redis_connection

from base.config import  EmailConfig,AuthConfig


from ..models import UserTwoFactorAuthSetting
from ..cache_key import (
        REDIS_ACCOUNT_FORGOT_PASSWORD_PREFIX,
        REDIS_ACCOUNT_FORGOT_PASSWORD_LOCK_PREFIX,
        REDIS_ACCOUNT_FORGOT_PASSWORD_ENCRYPT_KEY_PREFIX
    )

from ..utils import generate_code,hash_email,convert_seconds_to_minutes
from ..tasks import send_mail_otp_forgot_password
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()
con = get_redis_connection("user_app")
logger = logging.getLogger(__name__)

auth_config = AuthConfig().get_auth_config()
OTP_EXPIRES_LIFETIME = auth_config['OTP_EXPIRES_LIFETIME']
OTP_RENEW_WINDOW_LIFETIME = auth_config['OTP_RENEW_WINDOW_LIFETIME']

email_config = EmailConfig().get_email_service_config()


class UserForgotPasswordService:
    @staticmethod
    def validate_user_email(email):
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Email is already registered.'))
        except Exception as e:
            logger.error(f"An error occurred while validating user email: {e}")
            raise AuthenticationFailed(_('An error occurred, please try again.'))

    @staticmethod
    def set_email_otp_forgot_password(hashed_email, otp_code, ex=OTP_EXPIRES_LIFETIME):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_PREFIX}:{hashed_email}'
        con.set(key, otp_code, ex=ex)

    @staticmethod
    def get_email_otp_forgot_password(hashed_email):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_PREFIX}:{hashed_email}'
        return con.get(key)

    @staticmethod
    def lock_email_otp_forgot_password(hashed_email, ex=OTP_RENEW_WINDOW_LIFETIME):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_LOCK_PREFIX}:{hashed_email}'
        con.setbit(key, 0, 1)
        if ex is not None:
            con.expire(key, ex)

    @staticmethod
    def get_lock_email_otp_forgot_password_ttl(hashed_email):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_LOCK_PREFIX}:{hashed_email}'
        return con.ttl(key)

    @staticmethod
    def check_email_otp_forgot_password_is_locked(hashed_email):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_LOCK_PREFIX}:{hashed_email}'
        return con.exists(key)

    @staticmethod
    def set_email_forgot_password_key_encrypt(hashed_email, secret_key,
                                              ex=OTP_EXPIRES_LIFETIME):  # ex same as func set_email_otp_forgot_password
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_ENCRYPT_KEY_PREFIX}:{hashed_email}'
        con.set(key, secret_key, ex=ex)

    @staticmethod
    def get_email_forgot_password_key_encrypt(hashed_email):
        key = f'{REDIS_ACCOUNT_FORGOT_PASSWORD_ENCRYPT_KEY_PREFIX}:{hashed_email}'
        return con.get(key)

    @staticmethod
    def get_list_user_2fa_enabled(user) -> list:
        two_factor_auth_type = UserTwoFactorAuthSetting.objects.filter(user=user).values('type', 'is_enable',
                                                                                      'is_priority')
        if len(two_factor_auth_type) == 0:
            raise AuthenticationFailed(
                _('Two factor authentication is not enabled. Please contact support for assistance.'))
        list_two_factor_auth_type = []
        for value in two_factor_auth_type:
            if value['is_enable']:
                if (not email_config or email_config is None) and value['type'] == 'email':
                    continue
                list_two_factor_auth_type.append(value)
        if len(list_two_factor_auth_type) == 0:
            raise AuthenticationFailed(
                _('Two factor authentication is not enabled. Please contact support for assistance.'))
        return list_two_factor_auth_type

    @staticmethod
    def check_status_lock_email_forgot_password_otp(email) -> None:
        hashed_email = hash_email(email)
        if UserForgotPasswordService.check_email_otp_forgot_password_is_locked(hash_email):
            raise AuthenticationFailed(
                _(f'Cannot get new OTP. Please try again after {UserForgotPasswordService.get_lock_email_otp_forgot_password_ttl(hashed_email)} seconds.'))

    @staticmethod
    def create_email_secret_key(email):
        hashed_email = hash_email(email)
        secret_key = Fernet.generate_key().decode('utf-8')
        UserForgotPasswordService.set_email_forgot_password_key_encrypt(hashed_email, secret_key)
        return secret_key

    @staticmethod
    def decrypt_data_secret_key(data, secret_key):
        fernet = Fernet(secret_key.encode('utf-8'))
        decrypted_data = fernet.decrypt(data.encode('utf-8')).decode('utf-8')
        return json.loads(decrypted_data)

    @staticmethod
    def encrypt_data_secret_key(data, secret_key):
        fernet = Fernet(secret_key.encode('utf-8'))
        encrypted_data = fernet.encrypt(data.encode('utf-8')).decode('utf-8')
        return json.loads(encrypted_data)

    @staticmethod
    def create_email_otp_forgot_password(email, user_id, current_language_code):
        UserForgotPasswordService.check_status_lock_email_forgot_password_otp(email)
        hashed_email = hash_email(email)
        otp = generate_code()
        UserForgotPasswordService.set_email_otp_forgot_password(hashed_email, otp)
        send_mail_otp_forgot_password.delay(
            subject=_("Your Password Reset Code"),
            user_id=user_id,
            otp_code=otp,
            otp_expiry_minutes=convert_seconds_to_minutes(OTP_EXPIRES_LIFETIME),
            current_language_code=current_language_code)