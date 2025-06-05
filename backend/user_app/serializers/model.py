from ..models import User,Profile,Address,TOTP,UserTwoFactorAuthSetting,Oauth2Token, UserDeactivateReason
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class TOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = TOTP
        fields = '__all__'

class UserTwoFactorAuthTypeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='get_type_display', read_only=True)
    class Meta:
        model = UserTwoFactorAuthSetting
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='profile.first_name',required=False)
    last_name = serializers.CharField(source='profile.last_name',required=False)
    birth_day = serializers.CharField(source='profile.birth_day',required=False)
    gender = serializers.SerializerMethodField(required=False)
    address = AddressSerializer(many=True,required=False)
    enabled_2fa = serializers.SerializerMethodField(required=False)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = '__all__'

    def get_gender(self, obj) -> str:
        if not hasattr(obj, 'profile'):
            return None
        if obj.profile.gender == 1:
            return _('Male')
        elif obj.profile.gender == 2:
            return _('Female')
        elif obj.profile.gender == 3:
            return _('Other')
        elif obj.profile.gender == 0:
            return _('Not Say')
        return _('Unknown gender')

    def get_enabled_2fa(self,obj) -> list:
        if not hasattr(obj,'two_factor_auth_setting'):
            return
        enabled_2fa_objects = obj.two_factor_auth_setting.filter(is_enable=True)

        result = []
        for setting_obj in enabled_2fa_objects:
            result.append({
                'type': setting_obj.type,
                'is_priority': setting_obj.is_priority,
                'display': setting_obj.get_type_display()
            })

        return result
