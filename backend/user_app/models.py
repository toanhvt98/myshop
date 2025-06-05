from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField
import pyotp
import uuid
from base.models import BaseModelMixin


# Create your models here.

class GenderChoices(models.IntegerChoices):
    MALE = 1
    FEMALE = 2
    OTHER = 3
    NOT_SAY = 0

class TwoFactorAuthTypeChoices(models.TextChoices):
    TOPT = 'totp', _('2FA App')
    EMAIL = 'email', _('Email OTP')

class DeactivateUserReasonTypeChoices(models.TextChoices):
    SPAM = 'SPAM', _('Suspicious Spam Activity')
    ABUSE = 'ABUSE', _('Violation of Terms of Service')
    FROZEN_BY_ADMIN = 'ADMIN', _('Frozen by Administrator')
    TOO_MANY_FAILED_LOGINS = 'FAILED_LOGIN', _('Too many failed login attempts')
    INACTIVE = 'INACTIVE', _('User Inactive for too long')
    OTHER = 'OTHER', _('Other')

class DeactivateUserReasonActorDetailChoices(models.TextChoices):
    SYSTEM = 'system', _('System')
    ADMIN = 'admin', _('Admin')
    STAFF = 'staff', _('Staff')
    OTHER = 'other', _('Other')

class UserManage(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email không được để trống')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    email = models.EmailField(unique=True, max_length=100, verbose_name='Email')
    is_verification = models.BooleanField(default=False, verbose_name='Verification status')
    is_active = models.BooleanField(default=True, verbose_name='Active status')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')
    is_superuser = models.BooleanField(default=False, verbose_name='Is Superuser')

    objects = UserManage()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        indexes = [models.Index(fields=['email'])]
        verbose_name = 'User'
        verbose_name_plural = 'User'

    def update_last_login(self, *args, **kwargs):
        from django.utils import timezone
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])



class UserTwoFactorAuthSetting(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='two_factor_auth_setting',verbose_name='User')
    type = models.CharField(max_length=50,choices=TwoFactorAuthTypeChoices.choices,verbose_name='Type 2FA: TOTP or Email')
    is_enable = models.BooleanField(default=False,verbose_name='Enable 2FA')
    is_priority = models.BooleanField(default=False,verbose_name='Priority 2FA')
    class Meta:
        unique_together = ['user', 'type']
        verbose_name = 'User 2FA setting'
        verbose_name_plural = 'User 2FA setting'

class UserDeactivateReason(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deactivate_reason',verbose_name='User')
    reason_type = models.CharField(max_length=50,choices=DeactivateUserReasonTypeChoices.choices,verbose_name='Reason')
    reason_detail = models.CharField(max_length=500,null=True,blank=True,verbose_name='Detail')
    actor = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_deactivate',null=True,blank=True,default=None,verbose_name='Actor')
    reason_actor_detail = models.CharField(max_length=50,choices=DeactivateUserReasonActorDetailChoices.choices,verbose_name='Actor Detail')
    class Meta:
        verbose_name = 'User Deactivate Reason'
        verbose_name_plural = 'User Deactivate Reason'
        ordering = ['-created_at']


class Profile(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',verbose_name='User')
    phone_number = models.CharField(max_length=15,verbose_name='Phone number')
    first_name = models.CharField(max_length=50,verbose_name='First name')
    last_name = models.CharField(max_length=50,verbose_name='Last name')
    birth_date = models.DateField(null=True,blank=True,verbose_name='Birth date')
    gender = models.IntegerField(choices=GenderChoices.choices, default=GenderChoices.NOT_SAY,verbose_name='Gender')

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profile'

class Address(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address',verbose_name='User')
    province = models.CharField(max_length=50,verbose_name='Province')
    district = models.CharField(max_length=50,blank=True,null=True,verbose_name='District')
    ward = models.CharField(max_length=50,verbose_name='Ward')
    address = models.CharField(max_length=500,verbose_name='Address')
    is_default = models.BooleanField(default=False,verbose_name='Is default address')
    geo_location = models.CharField(max_length=500,null=True,blank=True,verbose_name='Geo location')

    class Meta:
        verbose_name = 'User Address'
        verbose_name_plural = 'User Address'


class TOTP(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='two_factor_auth',verbose_name='User')
    secret_key = EncryptedCharField(max_length=255,verbose_name='Secret Key')
    is_active = models.BooleanField(default=False,verbose_name='Is active')

    class Meta:
        verbose_name = '2FA Authentication'
        verbose_name_plural = '2FA Authentication'

    def check_otp(self, otp,digits):
        totp = pyotp.TOTP(self.secret_key,digits=digits)
        return totp.verify(otp)

class Oauth2Token(BaseModelMixin):
    id = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oauth2_token',verbose_name='User')
    access_token = EncryptedCharField(max_length=255,verbose_name='Access Token')
    refresh_token = EncryptedCharField(max_length=255,verbose_name='Refresh Token')
    expires_in = models.DateTimeField(verbose_name='Expires in')
    scope = models.CharField(max_length=255,verbose_name='Scope')

    class Meta:
        verbose_name = 'Token OAuth2'
        verbose_name_plural = 'Token OAuth2'