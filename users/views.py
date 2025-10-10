from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, OTP
from .serializers import UserSerializer, OTPVerifySerializer, ResetPasswordSerializer
from django.utils import timezone
import random
from .utils import send_otp_email
from clientProfiles.models import ClientProfile , ClientPhone

# ✅ Register
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # create client profile
            if user.user_type == 'client':
                ClientProfile.objects.create(user=user)
                ClientPhone.objects.create(user=user, phone_number=user.prime_phone)
            # generate and send OTP
            otp = OTP.objects.create(user=user, code=random.randint(1000,9999))
            send_otp_email(user.email, otp.code)
            return Response({"message":"OTP sent. Verify to activate account."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Verify OTP
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                otp_obj = OTP.objects.get(user__email=email, code=code)
                if otp_obj.is_expired():
                    return Response({"error":"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
                user = otp_obj.user
                user.is_active = True
                user.save()
                otp_obj.delete()
                return Response({"message":"Account verified successfully"}, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({"error":"Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_active:
                return Response({"error":"Account already verified"}, status=status.HTTP_400_BAD_REQUEST)
            otp_obj = OTP.objects.create(user=user, code=random.randint(1000,9999))
            send_otp_email(user.email, otp_obj.code)
            return Response({"message":"OTP resent successfully"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error":"User not found"}, status=status.HTTP_404_NOT_FOUND)

# ✅ Login
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        print(user)
        if user:
            if not user.is_active:
                return Response({"error":"Account not verified"}, status=status.HTTP_403_FORBIDDEN)
            refresh = RefreshToken.for_user(user)
            user.last_login = timezone.now()
            user.save()
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({"error":"Invalid User"})

# ✅ Forget Password
class ForgetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            otp_obj = OTP.objects.create(user=user, code=random.randint(1000,9999))
            send_otp_email(user.email, otp_obj.code)
            return Response({"message":"OTP sent to reset password"}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error":"User not found"}, status=status.HTTP_404_NOT_FOUND)

# ✅ Reset Password
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            try:
                otp_obj = OTP.objects.get(user__email=email, code=code)
                if otp_obj.is_expired():
                    return Response({"error":"OTP expired"}, status=status.HTTP_400_BAD_REQUEST)
                user = otp_obj.user
                user.set_password(new_password)
                user.save()
                otp_obj.delete()
                return Response({"message":"Password reset successfully"}, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({"error":"Invalid OTP or email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



