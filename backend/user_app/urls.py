from django.urls import path,include

# auth
from .views.authentication import (
    LoginApiView,
    MeApiView,
    VerifyLoginOtpApiView,
    RequestLoginOtpApiView,
    LogoutApiView,
    VerifyTotpLoginApiView,
)

url_authentication = [
    path('login/', LoginApiView.as_view(), name='login'),
    path('verify-otp-login/',VerifyLoginOtpApiView.as_view(),name='verify-otp-login'),
    path('verify-totp-login/',VerifyTotpLoginApiView.as_view(),name='verify-totp-login'),
    path('get-otp-login/',RequestLoginOtpApiView.as_view(),name='resend-otp-login'),
    path('me/', MeApiView.as_view(), name='me'),


    path('logout/', LogoutApiView.as_view(), name='logout'),

]

from .views.recovery_account import ForgotPasswordStepOneApiView,ForgotPasswordStepTwoApiView

url_recovery_account = [
    path('forgot-password-step-one/', ForgotPasswordStepOneApiView.as_view(), name='forgot-password-step-one'),
    path('forgot-password-step-two/', ForgotPasswordStepTwoApiView.as_view(), name='forgot-password-step-two'),
]

from .views.registration import RegisterApiView

url_registration = [
    path('register/', RegisterApiView.as_view(), name='register'),
]



# patterns
urlpatterns = [
    *url_authentication,
    *url_recovery_account,
    *url_registration,
]