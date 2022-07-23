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


class ClinicAdminSerializer(serializers.ModelSerializer):
    manager_details = serializers.SerializerMethodField('get_manager', read_only=True)

    def get_manager(self, clinic):
        return UserSerializer(clinic.manager, many=False).data

    class Meta:
        model = models.Clinic
        fields = '__all__'
        read_only_fields = [
            'creator'
        ]


class ClinicManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clinic
        fields = ['pk', 'title', 'address']


class ClinicGenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Clinic
        fields = '__all__'
        read_only_fields = ['title', 'manager', 'creator', 'address']


class SlotSerializer(serializers.ModelSerializer):
    clinic = ClinicManagerSerializer(many=False, read_only=True)

    class Meta:
        model = models.Slot
        fields = ['pk', 'date', 'time', 'number_of_appointments',
                  'clinic']
        read_only_fields = [
            'clinic'
        ]


class SlotCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slot
        fields = ['pk', 'date', 'time']


class AppointmentSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(many=False, read_only=True)

    class Meta:
        model = models.Appointment
        fields = '__all__'
        read_only_fields = [
            'status'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    patient = UserSerializer(many=False, read_only=True)

    class Meta:
        model = models.Appointment
        fields = '__all__'
        read_only_fields = [
            'status'
        ]


class ManagerAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Appointment
        fields = ['pk', 'status', 'patient', 'slot']
        read_only_fields = [
            'patient', 'slot', 'pk'
        ]


class CustomerSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Slot
        fields = ['pk', 'date', 'time']
