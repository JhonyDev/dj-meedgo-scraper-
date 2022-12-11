from rest_framework import serializers

from src.accounts.models import User
from . import models
from .models import Category


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
        fields = ['name', 'cost_per_night']


class CategoryNumSerializer(serializers.ModelSerializer):
    number_of_rooms = serializers.IntegerField()

    class Meta:
        model = models.Category
        fields = ['name', 'number_of_rooms', 'cost_per_night']

    def update(self, instance, validated_data):
        instance.name = self.validated_data['name']
        number = self.validated_data['number_of_rooms']
        cost_per_night = self.validated_data['cost_per_night']
        rooms = models.Room.objects.filter(category=instance)
        if rooms.count() < number:
            for x in range(number - rooms.count()):
                models.Room.objects.create(category=instance)
        elif rooms.count() > number:
            difference = rooms.count() - number
            removed = 0
            for x in rooms:
                if removed > difference:
                    pass
                else:
                    x.delete()
                    removed += 1
        rooms = models.Room.objects.filter(category=instance).count()
        instance.number_of_rooms = rooms
        instance.cost_per_night = cost_per_night
        instance.save()
        return instance


class CategoryPostSerializer(serializers.ModelSerializer):
    number_of_rooms = serializers.IntegerField()

    class Meta:
        model = models.Category
        fields = '__all__'

    def create(self, validated_data):
        name = self.validated_data['name']
        cost_per_night = self.validated_data['cost_per_night']
        category = Category.objects.filter(name=name)
        if not category.exists():
            category = Category(
                name=self.validated_data['name'],
                cost_per_night=cost_per_night
            )
            category.save()
        else:
            category = category.first()
        category.number_of_rooms = self.validated_data['number_of_rooms']
        return category


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Booking
        fields = [
            'created_on',
            'check_in_date',
            'check_out_date',
            'total_rooms',
            'customer_name',
            'company_name',
            'expected_number_of_people',
            'total_cost_of_bookings',
            'payment_type',
            'executive_per_night_cost',
            'deluxe_per_night_cost',
            'single',
            'double',
            'triple',
            'quad',
            'note',
            'customer_phone',
            'customer_email',
            'customer_cnic',
            'category',
            'options',
            'rooms',
            'per_night_cost',
            'manager',
            'is_active',
            'is_cancelled'
        ]
        read_only_fields = [
            'manager'
        ]


class NestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username'
        ]


class BookingPaymentSerializer(serializers.ModelSerializer):
    entry_by = NestUserSerializer(read_only=True)

    class Meta:
        model = models.BookingPayment
        fields = [
            'entry_by',
            'pk',
            'payment',
            'payment_date_time'
        ]
        read_only_fields = [
            'entry_by'
        ]
