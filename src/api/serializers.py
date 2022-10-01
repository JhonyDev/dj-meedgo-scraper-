from rest_framework import serializers

from src.accounts.models import User
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email',
            'is_superuser', 'is_staff', 'type', 'password'
        ]

        read_only_fields = [
            'date_joined', 'type', 'is_superuser', 'is_staff'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        print(password)
        user.set_password(password)
        user.save()
        return user


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['name']


class CategoryPostSerializer(serializers.ModelSerializer):
    number_of_rooms = serializers.IntegerField()

    class Meta:
        model = models.Category
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = '__all__'
        read_only_fields = [
            'is_active', 'manager'
        ]
