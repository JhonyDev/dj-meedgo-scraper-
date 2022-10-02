from rest_framework import serializers

from src.accounts.models import User
from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email',
            'is_superuser', 'is_staff', 'type', 'password', 'user_password'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }

        read_only_fields = [
            'date_joined', 'type', 'is_superuser', 'is_staff', 'user_password'
        ]

    def create(self, validated_data):
        user = User(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            user_password=self.validated_data['password'],
        )

        password = self.validated_data['password']
        print(password)

        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']
        instance.user_password = validated_data['password']
        password = validated_data['password']

        instance.set_password(password)
        instance.save()
        return instance


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
