from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException,ValidationError as VE

class AuthenticationFailed(APIException):
    status_code = 401
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'

class Throttled(APIException):
    status_code = 429
    default_detail = _('Request was throttled.')
    default_code = 'throttled'

class ValidationError(VE):
    status_code = 400
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self,detail=None,code=None):
        super().__init__(detail,code)