import logging

from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from base.exceptions import AuthenticationFailed
from ..models import Profile,UserTwoFactorAuthSetting,TwoFactorAuthTypeChoices

User = get_user_model()

logger = logging.getLogger(__name__)
class RegistrationService:
    @staticmethod
    @transaction.atomic
    def user_registration(email, password, first_name, last_name, language, phone_number, gender, birth_date):
        try:
            user = User.objects.create_user(email=email, password=password)
            logger.info(f"User {user.email} created successfully.")
        except IntegrityError:
            raise AuthenticationFailed(_('Email is already registered.'))
        except Exception as e:
            logger.error(f"An error occurred while creating user: {e}")
            raise AuthenticationFailed(_('Could not create user at this time.'))
        try:
            profile = Profile.objects.create(user=user, first_name=first_name, last_name=last_name, language=language,
                                             phone_number=phone_number, gender=gender, birth_date=birth_date)
            logger.info(f"Profile for user {user.email} created successfully.")
        except Exception as e:
            logger.error(f"An error occurred while creating profile for user {user.email}: {e}")
            raise AuthenticationFailed(_('An error occurred, please register again.'))
        try:
            two_factor_auth_type_create = []
            for value, label in TwoFactorAuthTypeChoices.choices:
                two_factor_auth_type_create.append(UserTwoFactorAuthSetting(user=user, type=value))
            UserTwoFactorAuthSetting.objects.bulk_create(two_factor_auth_type_create)
            logger.info(f"Two factor auth types for user {user.email} created successfully.")
        except Exception as e:
            logger.error(f"An error occurred while creating two factor auth types for user {user.email}: {e}")
            raise AuthenticationFailed(_('An error occurred, please register again.'))
        return user