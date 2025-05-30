import logging

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django_redis import get_redis_connection

from rest_framework.exceptions import AuthenticationFailed,Throttled

from base.config import AuthConfig, EmailConfig

from ..cache_key import REDIS_OTP_ATTEMPT_PREFIX, REDIS_LOCKING_ACCOUNT_PREFIX,REDIS_OTP_CODE_PREFIX,REDIS_OTP_CODE_LOCK_PREFIX,REDIS_TOTP_ATTEMPT_PREFIX
from ..tasks import send_mail_login_failed_deactivate,send_email_otp_login
from ..models import UserDeactivateReason, DeactivateUserReasonTypeChoices, DeactivateUserReasonActorDetailChoices

from ..utils import hash_email, generate_code, convert_seconds_to_minutes

User = get_user_model()

con = get_redis_connection("user_app")

logger = logging.getLogger(__name__)

email_config = EmailConfig().get_email_service_config()

auth_config = AuthConfig().get_auth_config()
DEACTIVATE_ACCOUNT_ON_OTP_LIMIT = auth_config['DEACTIVATE_ACCOUNT_ON_OTP_LIMIT']
IS_DEACTIVATE = auth_config['IS_DEACTIVATE']
MAX_OTP_ATTEMPTS_THRESHOLD = auth_config['MAX_OTP_ATTEMPTS_THRESHOLD']
MAX_TOTP_ATTEMPTS_THRESHOLD = auth_config['MAX_TOTP_ATTEMPTS_THRESHOLD']

OTP_ATTEMPT_WINDOW_LIFETIME = auth_config['OTP_ATTEMPT_WINDOW_LIFETIME']
LOCKING_ACCOUNT_LIFETIME = auth_config['LOCKING_ACCOUNT_LIFETIME']

OTP_EXPIRES_LIFETIME = auth_config['OTP_EXPIRES_LIFETIME']
OTP_RENEW_WINDOW_LIFETIME = auth_config['OTP_RENEW_WINDOW_LIFETIME']


class AuthenticationService:
    @staticmethod
    def increment_otp_attempts(hashed_email, ex=OTP_ATTEMPT_WINDOW_LIFETIME):
        key = f'{REDIS_OTP_ATTEMPT_PREFIX}:{hashed_email}'
        current_attempts = con.incr(key)
        con.expire(key, ex)
        return current_attempts

    @staticmethod
    def clear_otp_attempts(hashed_email):
        key = f'{REDIS_OTP_ATTEMPT_PREFIX}:{hashed_email}'
        con.delete(key)

    @staticmethod
    def lock_user_account(hashed_email, ex=LOCKING_ACCOUNT_LIFETIME):
        key = f'{REDIS_LOCKING_ACCOUNT_PREFIX}:{hashed_email}'
        con.set(key, 1, ex=ex, nx=True)

    @staticmethod
    def unlock_user_account(hashed_email):
        key = f'{REDIS_LOCKING_ACCOUNT_PREFIX}:{hashed_email}'
        con.delete(key)

    @staticmethod
    def is_account_locked(hashed_email):
        key = f'{REDIS_LOCKING_ACCOUNT_PREFIX}:{hashed_email}'
        return con.exists(key)

    @staticmethod
    def get_account_lock_remaining_time(hashed_email):
        key = f'{REDIS_LOCKING_ACCOUNT_PREFIX}:{hashed_email}'
        return con.ttl(key)

    @staticmethod
    def store_otp_code(hashed_email, otp_code, ex=OTP_EXPIRES_LIFETIME):
        key = f'{REDIS_OTP_CODE_PREFIX}:{hashed_email}'
        con.set(key, otp_code, ex=ex)

    @staticmethod
    def retrieve_otp_code(hashed_email):
        key = f'{REDIS_OTP_CODE_PREFIX}:{hashed_email}'
        return str(con.get(key).decode('utf-8'))

    @staticmethod
    def get_otp_expiry_time(hashed_email):
        key = f'{REDIS_OTP_CODE_PREFIX}:{hashed_email}'
        return con.ttl(key)

    @staticmethod
    def set_otp_rate_limit(hashed_email, ex=OTP_RENEW_WINDOW_LIFETIME):
        key = f'{REDIS_OTP_CODE_LOCK_PREFIX}:{hashed_email}'
        con.set(key, 1, ex=ex, nx=True)

    @staticmethod
    def is_otp_rate_limited(hashed_email):
        key = f'{REDIS_OTP_CODE_LOCK_PREFIX}:{hashed_email}'
        return con.exists(key)

    @staticmethod
    def increment_otp_request_count(hashed_email):
        key = f'{REDIS_OTP_CODE_LOCK_PREFIX}:{hashed_email}'
        con.incr(key)

    @staticmethod
    def get_otp_rate_limit_remaining_time(hashed_email):
        key = f'{REDIS_OTP_CODE_LOCK_PREFIX}:{hashed_email}'
        return con.ttl(key)

    @staticmethod
    def get_otp_request_count(hashed_email):
        key = f'{REDIS_OTP_CODE_LOCK_PREFIX}:{hashed_email}'
        count_bytes = con.get(key)

        if count_bytes:
            try:
                return int(count_bytes.decode('utf-8'))
            except ValueError:
                logger.warning(f"Invalid count value in Redis for key '{key}': {count_bytes}. Returning 0.")
                return 0
        return 0

    @staticmethod
    def increment_totp_attempts(hashed_email,ex=REDIS_TOTP_ATTEMPT_PREFIX):
        key = f'{REDIS_TOTP_ATTEMPT_PREFIX}:{hashed_email}'
        current_attempts = con.incr(key)
        con.expire(key,ex)
        return current_attempts

    @staticmethod
    def clear_totp_attempts(hashed_email):
        key = f'{REDIS_TOTP_ATTEMPT_PREFIX}:{hashed_email}'
        con.delete(key)

    @staticmethod
    def generate_and_send_otp(email,user_id,current_language_code):
        hashed_email = AuthenticationService.verify_account_status(email)
        AuthenticationService.verify_otp_rate_limit(hashed_email)
        otp = generate_code()
        with transaction.atomic():
            AuthenticationService.store_otp_code(hashed_email, otp)
            transaction.on_commit(
                lambda :send_email_otp_login.delay(
                    subject=_("Your Password Reset Code"),
                    user_id=user_id,
                    otp_code=otp,
                    otp_expiry_minutes=convert_seconds_to_minutes(OTP_EXPIRES_LIFETIME),
                    current_language_code=current_language_code,
                )
            )
            AuthenticationService.set_otp_rate_limit(hashed_email)
            AuthenticationService.increment_otp_request_count(hashed_email)
    @staticmethod
    def resend_otp(email,user_id,current_language_code):
        hashed_email = AuthenticationService.verify_account_status(email)
        AuthenticationService.verify_otp_rate_limit(hashed_email)
        AuthenticationService.increment_otp_request_count(hashed_email)
        AuthenticationService.generate_and_send_otp(email,user_id,current_language_code)
        return True


    @staticmethod
    def verify_otp(email, otp_code,current_language_code):
        hashed_email = AuthenticationService.verify_account_status(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Invalid credentials'))

        if not user.is_active or hasattr(user, 'deactivate_reason'):
            raise AuthenticationFailed(_('Your account has already been deactivated. Please contact support.'))

        if AuthenticationService.get_otp_expiry_time(hashed_email) is None:
            raise AuthenticationFailed(_('OTP was expired. Please try again.'))
        is_valid_otp = AuthenticationService.retrieve_otp_code(hashed_email) == otp_code
        if not is_valid_otp:
            current_attempts = AuthenticationService.increment_otp_attempts(hashed_email)
            if DEACTIVATE_ACCOUNT_ON_OTP_LIMIT:
                if current_attempts >= MAX_OTP_ATTEMPTS_THRESHOLD:
                    AuthenticationService.clear_otp_attempts(hashed_email)
                    if IS_DEACTIVATE:
                        try:
                            with transaction.atomic():
                                user_deactive = User.objects.select_for_update().get(email=email)
                                if not user.is_active:
                                    logger.info(f"User {user_deactive.email} was already deactivated by another process.")
                                    raise AuthenticationFailed(
                                        _('Your account has already been deactivated. Please contact support.'))
                                if UserDeactivateReason.objects.filter(user=user_deactive).exists():
                                    raise AuthenticationFailed(
                                        _('Your account has already been deactivated. Please contact support.'))


                                UserDeactivateReason.objects.create(
                                    user=user_deactive,
                                    reason_type=DeactivateUserReasonTypeChoices.SPAM,
                                    reason_actor_detail=DeactivateUserReasonActorDetailChoices.SYSTEM,
                                    reason_detail=_('Exceeded the number of allowed logins')
                                )

                                user_deactive.is_active = False
                                user_deactive.save()
                                transaction.on_commit(
                                    lambda: send_mail_login_failed_deactivate.delay(
                                        current_language_code=current_language_code,
                                        subject=_(
                                            'Your account has been deactivated!'),
                                        user_id=user_deactive.pk)
                                )
                        except Exception as e:
                            logger.error(f"An error occurred while deactivating user: {e}")
                            raise AuthenticationFailed(_('An error occurred, please try again'))
                        raise AuthenticationFailed(_('Your account has been deactivated. Please contact support.'))
                    else:
                        AuthenticationService.lock_user_account(hashed_email)
                        raise AuthenticationFailed(
                            _(f'Your account is locked. Please try again after {LOCKING_ACCOUNT_LIFETIME} seconds.'))
                else:
                    attempts_left = MAX_OTP_ATTEMPTS_THRESHOLD - current_attempts
                    raise AuthenticationFailed(
                        _(f'Invalid credentials. Your account will be locked after {attempts_left} more attempts.'))
            raise AuthenticationFailed(_('Invalid credentials.'))
        AuthenticationService.clear_otp_attempts(hashed_email)
        user.update_last_login()
        return user

    @staticmethod
    def authenticate_with_password(email, password) -> object:
        hashed_email = AuthenticationService.verify_account_status(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Invalid credentials'))

        if not user.is_active or hasattr(user, 'deactivate_reason'):
            raise AuthenticationFailed(_('Your account has already been deactivated. Please contact support.'))

        authenticated_user = authenticate(username=email, password=password)
        if authenticated_user is None:
            raise AuthenticationFailed(_('Invalid credentials'))
        authenticated_user.update_last_login()
        return authenticated_user

    @staticmethod
    def verify_totp(email, otp_code,current_language_code):
        hashed_email = AuthenticationService.verify_account_status(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(_('Invalid credentials'))
        if not user.is_active or hasattr(user, 'deactivate_reason'):
            raise AuthenticationFailed(_('Your account has already been deactivated. Please contact support.'))

        if not hasattr(user, 'two_factor_auth'):
            raise AuthenticationFailed(_('Two factor authentication is not enabled. Please contact support.'))
        secret_key = user.two_factor_auth.secret_key
        if not secret_key:
            raise AuthenticationFailed(_('Two factor authentication is not enabled. Please contact support.'))
        check_code = user.two_factor_auth.check_otp(otp_code)
        if not check_code:
            current_attempts = AuthenticationService.increment_totp_attempts(hashed_email)
            if DEACTIVATE_ACCOUNT_ON_OTP_LIMIT:
                if current_attempts >= MAX_TOTP_ATTEMPTS_THRESHOLD:
                    AuthenticationService.clear_totp_attempts(hashed_email)
                    if IS_DEACTIVATE:
                        try:
                            with transaction.atomic():
                                user_deactive = User.objects.select_for_update().get(email=email)
                                if not user.is_active:
                                    logger.info(
                                        f"User {user_deactive.email} was already deactivated by another process.")
                                    raise AuthenticationFailed(
                                        _('Your account has already been deactivated. Please contact support.'))
                                if UserDeactivateReason.objects.filter(user=user_deactive).exists():
                                    raise AuthenticationFailed(
                                        _('Your account has already been deactivated. Please contact support.'))

                                UserDeactivateReason.objects.create(
                                    user=user_deactive,
                                    reason_type=DeactivateUserReasonTypeChoices.SPAM,
                                    reason_actor_detail=DeactivateUserReasonActorDetailChoices.SYSTEM,
                                    reason_detail=_('Exceeded the number of allowed logins')
                                )

                                user_deactive.is_active = False
                                user_deactive.save()
                                transaction.on_commit(
                                    lambda: send_mail_login_failed_deactivate.delay(
                                        current_language_code=current_language_code,
                                        subject=_(
                                            'Your account has been deactivated!'),
                                        user_id=user_deactive.pk)
                                )
                        except Exception as e:
                            logger.error(f"An error occurred while deactivating user: {e}")
                            raise AuthenticationFailed(_('An error occurred, please try again'))
                        raise AuthenticationFailed(_('Your account has been deactivated. Please contact support.'))
                    else:
                        AuthenticationService.lock_user_account(hashed_email)
                        raise AuthenticationFailed(
                            _(f'Your account is locked. Please try again after {LOCKING_ACCOUNT_LIFETIME} seconds.'))
                else:
                    attempts_left = MAX_OTP_ATTEMPTS_THRESHOLD - current_attempts
                    raise AuthenticationFailed(
                        _(f'Invalid credentials. Your account will be locked after {attempts_left} more attempts.'))
            raise AuthenticationFailed(_('Invalid credentials.'))
        AuthenticationService.clear_totp_attempts(hashed_email)
        user.update_last_login()
        return user


    @staticmethod
    def verify_account_status(email):
        hashed_email = hash_email(email)
        if AuthenticationService.is_account_locked(hashed_email):
            if IS_DEACTIVATE:
                raise AuthenticationFailed(_('Your account has been deactivated. Please contact support.'))
            else:
                raise Throttled(
                    detail=_('Your account is locked. Please try again after {wait} seconds.'),wait=AuthenticationService.get_account_lock_remaining_time(hashed_email))
        return hashed_email

    @staticmethod
    def verify_otp_rate_limit(hashed_email):
        if AuthenticationService.is_otp_rate_limited(hashed_email) and AuthenticationService.get_otp_request_count(hashed_email) > 3:
            raise Throttled(detail=_(f'Cannot receive OTP at this time. Please try again after {AuthenticationService.get_otp_rate_limit_remaining_time(hashed_email)} seconds.'))

