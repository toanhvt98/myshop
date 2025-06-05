from django.urls import path,include

# auth
from .views.authentication import (
    SignInApiView,
    MeApiView,
    VerifySignInOtpApiView,
    RequestSignInOtpApiView,
    SignOutApiView,
)

url_authentication = [
    path('sign-in/', SignInApiView.as_view(), name='sign-in'),
    path('verify-sign-in-otp/',VerifySignInOtpApiView.as_view(),name='verify-sign-in-otp'),
    path('request-sign-in-otp/',RequestSignInOtpApiView.as_view(),name='request-sign-in-otp'),
    path('me/', MeApiView.as_view(), name='me'),


    path('sign-out/', SignOutApiView.as_view(), name='sign-out'),

]

from .views.recovery_account import ForgotPasswordStepOneApiView,ForgotPasswordStepTwoApiView

url_recovery_account = [
    path('forgot-password-step-one/', ForgotPasswordStepOneApiView.as_view(), name='forgot-password-step-one'),
    path('forgot-password-step-two/', ForgotPasswordStepTwoApiView.as_view(), name='forgot-password-step-two'),
]

from .views.registration import SignUpApiView

url_registration = [
    path('sign-up/', SignUpApiView.as_view(), name='sign-up'),
]



# patterns
urlpatterns = [
    *url_authentication,
    *url_recovery_account,
    *url_registration,
]