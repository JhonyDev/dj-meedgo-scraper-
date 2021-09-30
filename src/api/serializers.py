from rest_framework import serializers

from src.accounts.models import User
        

class UserPasswordChangeSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email', 'phone_number', 'profile_image',
            'likes','friends','address','date_joined', 'last_login'
        ]
        read_only_fields = [
            'email', 'profile_image', 'date_joined', 'last_login', 'username'
        ]


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']

