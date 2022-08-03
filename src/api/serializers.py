import uuid

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


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Images
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    slot = SlotSerializer(many=False, read_only=True)
    patient = UserSerializer(many=False, read_only=True)
    id_images = serializers.SerializerMethodField(read_only=True)
    insurance_images = serializers.SerializerMethodField(read_only=True)

    def get_id_images(self, obj):
        images = models.Images.objects.filter(image_type="ID", appointment=obj)
        return ImageSerializer(images, many=True).data

    def get_insurance_images(self, obj):
        images = models.Images.objects.filter(image_type="Insurance", appointment=obj)
        return ImageSerializer(images, many=True).data

    class Meta:
        model = models.Appointment
        fields = ['pk', 'patient', 'slot', 'status', 'id_images', 'insurance_images']
        read_only_fields = [
            'status'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    id_images = serializers.ListField(
        child=serializers.FileField(max_length=100000,
                                    allow_empty_file=False,
                                    use_url=True), write_only=True)
    insurance_images = serializers.ListField(
        child=serializers.FileField(max_length=100000,
                                    allow_empty_file=False,
                                    use_url=True), write_only=True)

    class Meta:
        model = models.Appointment
        fields = '__all__'
        read_only_fields = [
            'status'
        ]

    def create(self, validated_data):
        print(validated_data)
        id_images = validated_data.pop('id_images')
        insurance_images = validated_data.pop('insurance_images')
        print(validated_data)

        appointment = models.Appointment.objects.create(**validated_data)

        for img in id_images:
            models.Images.objects.create(image=img, image_type="ID", appointment=appointment)

        for img in insurance_images:
            models.Images.objects.create(image=img, image_type="Insurance", appointment=appointment)
        return appointment


def create(self, **kwargs):
    validated_data = self.validated_data
    print(validated_data)
    id_images = validated_data.pop('id_images')
    insurance_images = validated_data.pop('insurance_images')
    print(validated_data)

    appointment = models.Appointment.objects.create(**validated_data)

    for img in id_images:
        models.Images.objects.create(image=img, image_type="ID", appointment=appointment)

    for img in insurance_images:
        models.Images.objects.create(image=img, image_type="Insurance", appointment=appointment)

    return super().save(**kwargs)


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


class AppointmentCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Appointment
        fields = ['slot', 'status', 'patient']


class UserChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'date_of_birth', 'relation'
        ]

    def create(self, validated_data):
        email = f"{str(uuid.uuid4())[:5]}@{str(uuid.uuid4())[:4]}.com"
        username = f"{str(uuid.uuid4())[:5]}"
        return User.objects.create(email=email, username=username, **validated_data)
