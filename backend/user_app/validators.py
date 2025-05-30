from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
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