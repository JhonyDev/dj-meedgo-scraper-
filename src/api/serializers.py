from rest_framework import serializers

from src.accounts.models import User
from .models import Medicine, MedicineCart, OrderRequest, GrabUserBridge, MedicineOfferBridge


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
        fields = ['pk', 'medicines']


class OrderRequestCreateSerializer(serializers.ModelSerializer):
    # medicine_cart = MedicineCartSerializer()

    class Meta:
        model = OrderRequest
        fields = ['medicine_cart']


class OrderRequestListSerializer(serializers.ModelSerializer):
    medicine_cart = MedicineCartSerializer()

    class Meta:
        model = OrderRequest
        fields = ['pk', 'medicine_cart']


class GrabbedOrderRequestsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrabUserBridge
        fields = ['order_request']


class GrabbedOrderRequestsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrabUserBridge
        fields = ['is_active']


class MedicineOfferSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer()

    class Meta:
        model = MedicineOfferBridge
        fields = ['pk', 'medicine', 'offered_price']


class MedicineOfferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineOfferBridge
        fields = ['offered_price']


class GrabbedOrderRequestsListSerializer(serializers.ModelSerializer):
    # order_request = OrderRequestListSerializer()
    medicine_offers = serializers.SerializerMethodField('get_medicine_offers')
    offered_total_price = serializers.SerializerMethodField('get_offered_total')

    def get_medicine_offers(self, q):
        return MedicineOfferSerializer(MedicineOfferBridge.objects.filter(order_grab=q), many=True).data

    def get_offered_total(self, q):
        return sum(
            MedicineOfferBridge.objects.filter(
                order_grab=q).exclude(offered_price=None).values_list('offered_price', flat=True))

    class Meta:
        model = GrabUserBridge
        fields = ['pk', 'order_request', 'medicine_offers', 'offered_total_price', 'is_active']


""" SIMPLE SERIALIZERS """


class MedicineToCartSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField(required=False)
    cart_id = serializers.IntegerField(required=False)


class AlternateMedicineSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField(required=False)
