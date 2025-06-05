from base.views import AuthBaseView
from ..serializers import  SignUpSerializer,UserSerializer
from ..services import RegistrationService
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

class SignUpApiView(AuthBaseView):
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = SignUpSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data_copy = serializer.validated_data.copy()
        if 'password_confirmation' in validated_data_copy:
            validated_data_copy.pop('password_confirmation')
        user = RegistrationService.user_registration(**validated_data_copy)
        user_serializer = UserSerializer(user)
        refresh_token = RefreshToken.for_user(user)
        request._new_access_token = str(refresh_token.access_token)
        request._new_refresh_token = str(refresh_token)
        return Response(user_serializer.data,status=201)