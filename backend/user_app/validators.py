from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from base.config import AuthConfig

auth_config = AuthConfig().get_auth_config()

def password_regex_validator(value):
    django_regex_validator_instance = RegexValidator(
        regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[\S]{8,}$',
        message=_(
            "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character (@, $, !, %, *, #, ?, &.).")
    )
    try:
        django_regex_validator_instance(value)
    except Exception as e:
        raise ValidationError(e.message)

def only_characters_regex_validator(value):
    django_regex_validator_instance = RegexValidator(
        regex=r'^[a-zA-Z]+$',
        message=_(
            "Only characters and spaces are allowed.")
    )
    try:
        django_regex_validator_instance(value)
    except Exception as e:
        raise ValidationError(e.message)

def phone_regex_validator(value):
    django_regex_validator_instance = RegexValidator(
        regex=r'^\+[1-9]\d{1,3}\s?\d{7,15}$',
        message=_(
            "Phone number must start with '+', followed by country code (1-4 digits), an optional space, and then 7-15 digits.")
    )
    try:
        django_regex_validator_instance(value)
    except Exception as e:
        raise ValidationError(e.message)

def otp_regex_validator(value):
    otp_digits = str(auth_config['OTP_LENGTH'])
    if auth_config['OTP_MIXED_CASE']:
        regex = r'^[0-9a-zA-Z]{' +otp_digits+ r'}$'
        mess = 'characters.'
    else:
        regex = r'^[0-9]{'+ otp_digits +r'}$'
        mess = 'digits.'
    django_regex_validator_instance = RegexValidator(
        regex=regex,
        message=_(
            f"OTP code must be {otp_digits} {mess}")
    )
    try:
        django_regex_validator_instance(value)
    except Exception as e:
        raise ValidationError(e.message)

def totp_regex_validator(value):
    totp_digits = str(auth_config['TOTP_DIGITS'])
    django_regex_validator_instance = RegexValidator(
        regex=r'^[0-9]{' + totp_digits + r'}$',
        message=_(
            f"TOTP code must be {totp_digits} digits.")
    )
    try:
        django_regex_validator_instance(value)
    except Exception as e:
        raise ValidationError(e.message)