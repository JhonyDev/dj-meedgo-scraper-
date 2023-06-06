from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from src.accounts.models import User, License, LicenseEntry


#
# class CustomRegisterAccountSerializer(serializers.ModelSerializer):
#     password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
#
#     class Meta:
#         model = User
#         fields = [
#             'pk', 'username', 'email', 'postal_code', 'password', 'password2'
#         ]
#         read_only_fields = [
#             'type'
#         ]
#         extra_kwargs = {
#             'password': {'write_only': True},
#         }
#
#     def save(self):
#         user = User(
#             # first_name=self.validated_data['first_name'],
#             # last_name=self.validated_data['last_name'],
#             email=self.validated_data['email'],
#             postal_code=self.validated_data['postal_code'],
#             username=self.validated_data['username'],
#         )
#         password = self.validated_data['password']
#         password2 = self.validated_data['password2']
#         email = self.validated_data['email']
#
#         if password != password2:
#             raise serializers.ValidationError({'password': 'Passwords must be matched'})
#         if EmailAddress.objects.filter(email=email):
#             raise serializers.ValidationError({'email': 'Email is already registered'})
#
#         user.set_password(password)
#         user.save()
#         return user
#

class CustomRegisterAccountSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'pk', 'full_name', 'username', 'email', 'postal_code', 'phone_number', 'password', 'password2'
        ]
        read_only_fields = [
            'type'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if not email and not username and not phone_number:
            raise serializers.ValidationError('Either email or username or phone_number must be provided.')

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email is already registered.'})

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'Username is already registered.'})

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({'phone_number': 'Phone Number is already registered.'})

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        return attrs

    def save(self, **kwargs):
        user = User(
            full_name=self.validated_data.get('full_name'),
            email=self.validated_data.get('email'),
            postal_code=self.validated_data.get('postal_code'),
            username=self.validated_data.get('username'),
            phone_number=self.validated_data.get('phone_number'),
        )
        password = self.validated_data.get('password')
        user.set_password(password)
        user.save()
        return user


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if not username and not email and not phone_number:
            raise serializers.ValidationError('Either email or username or phone_number must be provided.')

        user = authenticate(username=username, email=email, phone_number=phone_number, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid credentials.')

        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')

        attrs['user'] = user
        return attrs


class RegisterSerializerRestAPI(RegisterSerializer):
    phone_number = serializers.CharField(max_length=30)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        print(self.data)
        user.phone_number = self.data.get('phone_number')
        # user.profile_image = self.data.get('profile_image')
        user.save()
        return user


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'


class LicenseEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseEntry
        exclude = ('user',)


class PhoneOTPLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField()
