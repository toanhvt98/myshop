from django.utils import translation

from rest_framework.response import Response

from base.views import AuthBaseView

from ..serializers import  RecoveryAccountSerializer
from ..services import RecoveryAccountService


class ForgotPasswordStepOneApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        current_language_code = translation.get_language()
        data = request.data
        serializer = RecoveryAccountSerializer(data=data,context={'fields':['email']})
        serializer.is_valid(raise_exception=True)
        user = RecoveryAccountService.validate_user_email(**serializer.validated_data)
        RecoveryAccountService.create_email_otp_forgot_password(current_language_code=current_language_code,user_id=user.pk,**serializer.validated_data)
        user_2fa_enabled = RecoveryAccountService.get_list_user_2fa_enabled(user)
        return Response({'data':user_2fa_enabled},status=200)

# forgot password step 2
class ForgotPasswordStepTwoApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = RecoveryAccountSerializer(data=data,context={'fields':['type']})
        serializer.is_valid(raise_exception=True)
        return Response({'data':'success'},status=200)