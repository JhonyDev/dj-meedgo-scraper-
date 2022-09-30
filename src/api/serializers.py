from rest_framework import serializers

from src.accounts.models import User
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email',
            'is_superuser', 'is_staff', 'type'
        ]

        read_only_fields = [
            'date_joined', 'type', 'is_superuser', 'is_staff'
        ]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
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
