from random import choices

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from base.serializers import SerializerMixin,serializers
from base.config import AuthConfig

from ..validators import totp_regex_validator,otp_regex_validator

User = get_user_model()

auth_config = AuthConfig().get_auth_config()

class AuthenticationSerializer(SerializerMixin):
    email = serializers.EmailField(error_messages={
        'required': _('Email is required.'),
        'invalid': _('Please enter a valid email address.')}
    )
    password = serializers.CharField(
        error_messages={
            'required': _('Password is required.'),
        },
    )


class OtpAuthenticationSerializer(SerializerMixin):
    otp_code = serializers.CharField(
        error_messages={
            'required': _('OTP code is required.'),
        },
    )
    otp_type = serializers.ChoiceField(
        error_messages={
            'required': _('Type is required.'),
            'invalid_choice': _('Please enter a valid type.'),
        },
        choices=(('totp', _('TOTP')), ('email', _('Email OTP'))),
    )

    def validate(self, data):
        otp_type = data.get('otp_type')
        otp_code = data.get('otp_code')
        if not otp_type:
            raise serializers.ValidationError({"otp_type": _("OTP type is missing.")})
        if not otp_code:
            raise serializers.ValidationError({"otp_code": _("OTP code is missing.")})
        if otp_type == 'totp':
            totp_regex_validator(otp_code)
        elif otp_type == 'email':
            otp_regex_validator(otp_code)
        return data
