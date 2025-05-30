from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from base.serializers import SerializerMixin,serializers
from base.exceptions import ValidationError

from ..validators import only_characters_regex_validator,phone_regex_validator,password_regex_validator
from ..models import LanguageChoices,GenderChoices

User = get_user_model()

class RegisterSerializer(SerializerMixin):
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