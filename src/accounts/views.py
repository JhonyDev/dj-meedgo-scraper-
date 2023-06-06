import random
from datetime import datetime

from allauth.account.models import EmailAddress
from django_otp import devices_for_user
from rest_framework import generics, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from src.accounts import authentication
from src.accounts.authentication import JWTAuthentication
from src.accounts.models import License, LicenseEntry, User
from src.accounts.serializers import CustomRegisterAccountSerializer, CustomLoginSerializer, LicenseSerializer, \
    LicenseEntrySerializer, PhoneOTPLoginSerializer, OTPVerificationSerializer
from src.api.serializers import UserSerializer, UserProfileSerializer


class UserUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class CustomRegisterAccountView(APIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        status_code = status.HTTP_400_BAD_REQUEST
        serializer = CustomRegisterAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if user.email:
                EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            access_token = authentication.create_access_token(UserSerializer(user).data)
            refresh_token = authentication.create_refresh_token(user.pk)
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            status_code = status.HTTP_201_CREATED
        else:
            data = serializer.errors
        return Response(data=data, status=status_code)


class CustomLoginView(APIView):
    serializer_class = CustomLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        response = Response()
        user_serializer = UserSerializer(user)
        access_token = authentication.create_access_token(user_serializer.data)
        refresh_token = authentication.create_refresh_token(user.pk)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response


class LicensesListView(generics.ListAPIView):
    serializer_class = LicenseSerializer
    queryset = License.objects.all()
    permission_classes = [permissions.AllowAny]


class LicenseEntryListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = LicenseEntrySerializer
    queryset = LicenseEntry.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()


class LicenseEntryRUDView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = LicenseEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LicenseEntry.objects.all()


class PhoneOTPLoginView(generics.CreateAPIView):
    serializer_class = PhoneOTPLoginSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({'message': 'No Account associated with the registered phone number'},
                            status=status.HTTP_400_BAD_REQUEST)
        account_sid = 'ACc6f76e3f2985ee13d0c10aea70bb2f54'
        auth_token = '9eb77c755d1f6ddd3510a978c2d6e87a'
        twilio_number = '+13612667531'
        try:
            client = Client(account_sid, auth_token)
            otp = random.randint(1000, 9999)
            message = f"Your OTP is: {otp}"
            client.messages.create(
                body=message,
                from_=twilio_number,
                to=phone_number
            )
            user.otp_sent = True
            user.otp_secret = otp
            user.otp_created = datetime.now()
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Please check format. Expected format - "+9233xxxxxxxx"'},
                            status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        user = request.user

        otp_device = devices_for_user(user)[0]
        is_valid = otp_device.verify(otp)

        if is_valid:
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
