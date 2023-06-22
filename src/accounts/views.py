import random
import uuid
from datetime import datetime

import requests
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from django.contrib.auth.hashers import check_password
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from django_otp import devices_for_user
from rest_auth.registration.views import SocialLoginView
from rest_framework import generics, permissions, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from core import settings
from src.accounts import authentication
from src.accounts.authentication import JWTAuthentication
from src.accounts.models import License, LicenseEntry, User, UserTime, AuthenticationToken
from src.accounts.serializers import CustomRegisterAccountSerializer, CustomLoginSerializer, LicenseSerializer, \
    LicenseEntrySerializer, PhoneOTPLoginSerializer, OTPVerificationSerializer, UserTimeSerializer, \
    ChangePasswordSerializer, EmailVerificationSerializer, EmailVerificationStatusSerializer, \
    CustomGoogleLoginSerializerSerializer
from src.api.serializers import UserSerializer, UserProfileSerializer


class UserTimeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserTime.objects.all()
    serializer_class = UserTimeSerializer
    lookup_field = 'day'

    def perform_create(self, serializer):
        if not UserTime.objects.filter(user=self.request.user, day=serializer.validated_data['day']).exists():
            serializer.save(user=self.request.user)

    def get_queryset(self):
        return UserTime.objects.filter(user=self.request.user)


class UserUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class CustomRegisterAccountView(CreateAPIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if user.email:
            unique_id = str(uuid.uuid4())
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': settings.BASE_URL,
                'unique_id': unique_id,
            })
            email = EmailMultiAlternatives(mail_subject, message, to=[user.email])
            email.attach_alternative(message, 'text/html')
            email.send()
            # send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
            AuthenticationToken.objects.create(user=user, auth_token=unique_id)
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        # access_token = authentication.create_access_token(UserSerializer(user).data)
        # refresh_token = authentication.create_refresh_token(user.pk)
        data = {
            'message': f"Sign up successful, Verification email is sent to {user.email}.",
        }
        return Response(data=data, status=status.HTTP_201_CREATED)


class CustomLoginView(APIView):
    serializer_class = CustomLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        response = Response(status=status.HTTP_200_OK)
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

    def get_queryset(self):
        return LicenseEntry.objects.filter(user=self.request.user)

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


class ChangePasswordView(UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not check_password(old_password, self.request.user.password):
                return Response({'message': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            self.request.user.set_password(new_password)
            self.request.user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(View):
    def get(self, request, auth_token):
        auth_token = AuthenticationToken.objects.filter(auth_token=auth_token).first()
        if auth_token:
            auth_token.user.is_active = True
            auth_token.user.save()
            return render(request, 'accounts/ver_success.html')
        return render(request, 'accounts/ver_failed.html')


class ResendVerificationView(APIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        unique_id = str(uuid.uuid4())
        mail_subject = 'Activate your account'
        message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'domain': settings.BASE_URL,
            'unique_id': unique_id,
        })
        email = EmailMultiAlternatives(mail_subject, message, to=[user.email])
        email.attach_alternative(message, 'text/html')
        email.send()
        # send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        AuthenticationToken.objects.create(user=user, auth_token=unique_id)
        response = Response(status=status.HTTP_200_OK)
        response.data = {
            'message': f'Verification email is sent to {user.email}.'
        }
        return response


class VerificationStatusView(APIView):
    serializer_class = EmailVerificationStatusSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        response = Response(status=status.HTTP_200_OK)
        response.data = {
            'is_verified': user.is_active
        }
        return response


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        print(request.user)
        response = Response(status=status.HTTP_200_OK)
        response.data = {
            'message': 'verified'
        }
        return response


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class CustomGoogleSignInView(generics.ListCreateAPIView):
    serializer_class = CustomGoogleLoginSerializerSerializer
    permission_classes = [permissions.AllowAny]
    queryset = LicenseEntry.objects.all()

    def get(self, request, *args, **kwargs):
        data = {
            'message': request.GET,
        }
        return Response(data=data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        url = 'https://oauth2.googleapis.com/token'
        payload = {
            'code': code,
            'redirect_uri': f'https://meedgo.com/',
            'client_id': f'{settings.GOOGLE_CLIENT_ID}',
            'client_secret': f'{settings.GOOGLE_CLIENT_SECRET}',
            'scope': '',
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=payload)
        tokens = response.json()
        access_token = response.json().get('access_token')
        url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            profile_image = user_info.get('picture')
            full_name = user_info.get('name')
            email = user_info.get('email')
        else:
            data = {
                'details': tokens,
            }
            return Response(data=data, status=status.HTTP_201_CREATED)

        if User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.create(email=email, profile_image=profile_image, full_name=full_name)
        user_serializer = UserSerializer(user)
        access_token = authentication.create_access_token(user_serializer.data)
        refresh_token = authentication.create_refresh_token(user.pk)
        data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return Response(data=data, status=status.HTTP_201_CREATED)


class CustomFacebookSignInView(generics.ListCreateAPIView):
    serializer_class = CustomGoogleLoginSerializerSerializer
    permission_classes = [permissions.AllowAny]
    queryset = LicenseEntry.objects.all()

    def get(self, request, *args, **kwargs):
        data = {
            'message': request.GET,
        }
        return Response(data=data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        url = 'https://oauth2.googleapis.com/token'
        payload = {
            'code': code,
            'redirect_uri': f'{settings.BASE_URL}auth/custom/google/login/',
            'client_id': f'{settings.GOOGLE_CLIENT_ID}',
            'client_secret': f'{settings.GOOGLE_CLIENT_SECRET}',
            'scope': '',
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=payload)
        tokens = response.json()
        access_token = response.json().get('access_token')
        url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            profile_image = user_info.get('picture')
            full_name = user_info.get('name')
            email = user_info.get('email')
        else:
            data = {
                'details': tokens,
            }
            return Response(data=data, status=status.HTTP_201_CREATED)

        if User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email).first()
        else:
            user = User.objects.create(email=email, profile_image=profile_image, full_name=full_name)
        user_serializer = UserSerializer(user)
        access_token = authentication.create_access_token(user_serializer.data)
        refresh_token = authentication.create_refresh_token(user.pk)
        data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
