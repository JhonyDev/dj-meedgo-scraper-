from rest_framework import serializers

from src.accounts.models import User
from .models import Medicine, MedicineCart


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email',
            'is_superuser', 'is_staff', 'type', 'password'
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
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance


class MedicineSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = ['pk', 'name', 'salt_name', 'price', 'med_image', 'med_url', 'platform', 'is_available']

    def get_platform(self, obj):
        return obj.get_platform()


class MedicineCartSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True)

    class Meta:
        model = MedicineCart
        fields = ['id', 'medicines']


class MedicineToCartSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField(required=False)
    cart_id = serializers.IntegerField(required=False)

# class ServicesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Service
#         exclude = ('service_base_64',)

#
# class ServicesAllSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Service
#         fields = '__all__'
#
#
# class CategoryNumSerializer(serializers.ModelSerializer):
#     number_of_rooms = serializers.IntegerField()
#
#     class Meta:
#         model = models.Category
#         fields = ['name', 'number_of_rooms', 'cost_per_night']
#
#     def update(self, instance, validated_data):
#         instance.name = self.validated_data['name']
#         number = self.validated_data['number_of_rooms']
#         cost_per_night = self.validated_data['cost_per_night']
#         rooms = models.Room.objects.filter(category=instance)
#         if rooms.count() < number:
#             for x in range(number - rooms.count()):
#                 models.Room.objects.create(category=instance)
#         elif rooms.count() > number:
#             difference = rooms.count() - number
#             removed = 0
#             for x in rooms:
#                 if removed > difference:
#                     pass
#                 else:
#                     x.delete()
#                     removed += 1
#         rooms = models.Room.objects.filter(category=instance).count()
#         instance.number_of_rooms = rooms
#         instance.cost_per_night = cost_per_night
#         instance.save()
#         return instance
