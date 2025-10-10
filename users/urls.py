from django.urls import path
from .views import RegisterAPIView, VerifyOTPAPIView, LoginAPIView, ForgetPasswordAPIView, ResetPasswordAPIView, ResendOTPAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPAPIView.as_view(), name='resend-otp'), # when otp expire or reset password 
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forget-password/', ForgetPasswordAPIView.as_view(), name='forget-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
   
]
 