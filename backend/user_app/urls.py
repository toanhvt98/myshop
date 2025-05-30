from django.urls import path,include

# auth
from .views.auth import LoginApiView,RegisterApiView,MeApiView,ForgotPasswordStepOneApiView,VerifyLoginOtpApiView,ResendLoginOtpApiView
urlauth = [
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('me/', MeApiView.as_view(), name='me'),
    path('forgot-password-step-one/', ForgotPasswordStepOneApiView.as_view(), name='forgot-password-step-one'),
    path('verify-otp-login/',VerifyLoginOtpApiView.as_view(),name='verify-otp-login'),
    path('resend-otp-login/',ResendLoginOtpApiView.as_view(),name='resend-otp-login')

]



# patterns
urlpatterns = [
    path('auth/',  include((urlauth, 'auth'), namespace='auth')),
]