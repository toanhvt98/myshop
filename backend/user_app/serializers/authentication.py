
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
        validators=[otp_regex_validator]
    )

class TotpAuthenticationSerializer(SerializerMixin):
    totp_code = serializers.CharField(
        error_messages={
            'required': _('TOTP code is required.'),
        },
        validators=[totp_regex_validator]
    )
