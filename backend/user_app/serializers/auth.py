from random import choices

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from base.config import AuthConfig
from ..validators import password_regex_validator,only_characters_regex_validator,phone_regex_validator
from ..models import LanguageChoices,GenderChoices,TwoFactorAuthTypeChoices
User = get_user_model()

auth_config = AuthConfig().get_auth_config()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={
        'required': _('Email is required.'),
        'invalid': _('Please enter a valid email address.')}
    )
    password = serializers.CharField(
        error_messages={
            'required': _('Password is required.'),
        },
    )

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages={
        'required': _('Email is required.'),
        'invalid': _('Please enter a valid email address.')}
    )

    first_name = serializers.CharField(
        min_length=2,
        max_length=30,
        error_messages={
            'required': _('First name is required.'),
            'min_length': _('First name must be at least 2 characters long.'),
            'max_length': _('First name must be at most 30 characters long.'),
        },
        validators=[only_characters_regex_validator]
    )

    last_name = serializers.CharField(
        min_length=2,
        max_length=30,
        error_messages={
            'required': _('Last name is required.'),
            'min_length': _('Last name must be at least 2 characters long.'),
            'max_length': _('Last name must be at most 30 characters long.'),
        },
        validators=[only_characters_regex_validator]
    )

    birth_date = serializers.DateField(required=False,default=None,error_messages={'invalid': _('Please enter a valid date.')})
    language = serializers.ChoiceField(
        required=False,
        choices=LanguageChoices.choices,
        default=LanguageChoices.VI,
        error_messages={'invalid': _('Please enter a valid language.')}
    )
    gender = serializers.ChoiceField(
        required=False,
        choices=GenderChoices.choices,
        default=GenderChoices.NOT_SAY,
        error_messages={'invalid': _('Please enter a valid gender.')}
    )

    phone_number = serializers.CharField(
        min_length=10,
        max_length=15,
        validators=[phone_regex_validator]
    )

    password = serializers.CharField(
        error_messages={
            'required': _('Password is required.'),
        },
        validators=[password_regex_validator]
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('Password confirmation is required.'),
        },
    )

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise ValidationError(_('Passwords do not match.'))
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": _("This email is already registered.")})
        return data


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': _('Email is required.'),
            'invalid': _('Please enter a valid email address.')
        }
    )

class OtpLoginSerializer(serializers.Serializer):
    otp_code = serializers.CharField(
        min_length=auth_config['OTP_LENGTH'],
        max_length=auth_config['OTP_LENGTH'],
        error_messages={
            'required': _('OTP code is required.'),
            'min_length': _('OTP code must be at least {min_length} characters long.'),
            'max_length': _('OTP code must be at most {max_length} characters long.'),
        },
    )

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': _('Email is required.'),
            'invalid': _('Please enter a valid email address.')
        }
    )
    type = serializers.ChoiceField(
        required=True,
        choices=TwoFactorAuthTypeChoices.choices,
        error_messages={'invalid': _('Please enter a valid type.')}
    )
    otp_code = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('OTP code is required.'),
        },
    )
    new_password = serializers.CharField(
        error_messages={
            'required': _('New password is required.'),
        },
        validators=[password_regex_validator]
    )
    new_password_confirmation = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('New password confirmation is required.'),
        },
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        requested_fields = self.context.get('fields')

        if requested_fields:
            existing_fields = list(self.fields.keys())
            for field_name in existing_fields:
                if field_name not in requested_fields:
                    self.fields.pop(field_name)

    def validate(self, data):
        if 'new_password' in data and 'new_password_confirmation' in data:
            if data['new_password'] != data['new_password_confirmation']:
                raise ValidationError(_('Passwords do not match.'))
        return data

class ConfirmPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        error_messages={
            'required': _('Password is required.'),
        },
        validators=[password_regex_validator]
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        error_messages={
            'required': _('Password confirmation is required.'),
        },
    )

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise ValidationError(_('Passwords do not match.'))
        return data
