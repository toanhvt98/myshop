from django.utils.translation import gettext_lazy as _

from base.serializers import SerializerMixin,serializers
from base.exceptions import ValidationError

from ..models import TwoFactorAuthTypeChoices
from ..validators import password_regex_validator

class RecoveryAccountSerializer(SerializerMixin):
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

    def validate(self, data):
        if 'new_password' in data and 'new_password_confirmation' in data:
            if data['new_password'] != data['new_password_confirmation']:
                raise ValidationError(_('Passwords do not match.'))
        return data


class ConfirmPasswordRecoveryAccountSerializer(SerializerMixin):
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
