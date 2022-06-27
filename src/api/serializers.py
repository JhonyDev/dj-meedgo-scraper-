from rest_framework import serializers

from src.accounts.models import User
from . import models


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDetail
        fields = '__all__'
        read_only_fields = [
            'user'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'age', 'address',
            'is_superuser', 'is_staff', 'type', 'creator'
        ]
        read_only_fields = [
            'date_joined', 'creator', 'type', 'is_superuser', 'is_staff'
        ]


class ClinicSerializer(serializers.ModelSerializer):
    manager = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Clinic
        fields = '__all__'
        read_only_fields = [
            'manager'
        ]


class SlotSerializer(serializers.ModelSerializer):
    clinic = ClinicSerializer(many=False, read_only=True)

    class Meta:
        model = models.Slot
        fields = '__all__'
        read_only_fields = [
            'clinic'
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(many=False, read_only=True)
    patient = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Appointment
        fields = '__all__'


class ManagerAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Appointment
        fields = ['pk', 'status', 'patient', 'slot']
        read_only_fields = [
            'patient', 'slot', 'pk'
        ]
