from django.db.models import Sum
from rest_framework import serializers

from src.accounts.models import User
from .models import Medicine, MedicineCart, OrderRequest, GrabUserBridge, MedicineOfferBridge, MedicineCartBridge


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'username', 'email', 'phone_number',
            'is_staff', 'postal_code', 'password'
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
    price = serializers.SerializerMethodField('get_price')

    class Meta:
        model = Medicine
        fields = ['pk', 'name', 'salt_name', 'price', 'discounted_price', 'med_image', 'med_url', 'platform',
                  'is_available']

    def get_price(self, obj):
        return obj.price if obj.price is not None else obj.discounted_price

    def get_platform(self, obj):
        return obj.get_platform()


class MedicineCartSerializer(serializers.ModelSerializer):
    medicines = serializers.SerializerMethodField('get_meds')

    def get_meds(self, obj):
        all_bridges = MedicineCartBridge.objects.filter(
            medicine_card=obj, medicine__pk__in=obj.medicines.all().values_list('pk', flat=True))
        return MedicineCartBridgeSerializer(all_bridges, many=True).data

    class Meta:
        model = MedicineCart
        fields = ['pk', 'medicines']


class OrderRequestCreateSerializer(serializers.ModelSerializer):
    # medicine_cart = MedicineCartSerializer()

    class Meta:
        model = OrderRequest
        fields = ['medicine_cart']


class MedicineCartBridgeSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer()

    class Meta:
        model = MedicineCartBridge
        fields = ['quantity', 'medicine']


class OrderRequestListSerializer(serializers.ModelSerializer):
    medicine_cart = MedicineCartSerializer()

    class Meta:
        model = OrderRequest
        fields = ['pk', 'medicine_cart']


class LocalityOrderRequestListSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField('get_total_cost')

    def get_total_cost(self, q):
        return q.medicine_cart.medicines.aggregate(total=Sum('price'))['total']

    class Meta:
        model = OrderRequest
        fields = ['pk', 'total']


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
    cost_comparisons = serializers.SerializerMethodField('get_cost_comparisons')

    def get_cost_comparisons(self, q):
        from src.api.utils import LIST_PLATFORMS
        from src.api.utils import get_platform_dict
        platforms_list = []
        for platform in LIST_PLATFORMS:
            platform_medicines = Medicine.objects.filter(platform=get_platform_dict()[platform])
            missing_count = 0
            total_cost = 0
            for medicine in q.order_request.medicine_cart.medicines.all():
                query_set = platform_medicines.filter(
                    name=medicine.name, salt_name=medicine.salt_name, dosage=medicine.dosage)
                if not query_set.exists():
                    missing_count += 1
                else:
                    total_cost += query_set.first().price or 0
            platforms_list.append({
                'platform': platform,
                'total_cost': total_cost,
                'status': f'{missing_count} medicines are missing'
            })
        return platforms_list

    def get_medicine_offers(self, q):
        return MedicineOfferSerializer(MedicineOfferBridge.objects.filter(order_grab=q), many=True).data

    def get_offered_total(self, q):
        return sum(
            MedicineOfferBridge.objects.filter(
                order_grab=q).exclude(offered_price=None).values_list('offered_price', flat=True))

    class Meta:
        model = GrabUserBridge
        fields = ['pk', 'order_request', 'cost_comparisons', 'medicine_offers', 'offered_total_price', 'is_active']

    def get_fields(self):
        fields = super().get_fields()
        fields['order_request'].read_only = True
        fields['is_active'].read_only = True
        return fields


""" SIMPLE SERIALIZERS """


class MedicineToCartSerializer(serializers.Serializer):
    CHOICES = [
        ('ADD', 'ADD'),
        ('REMOVE', 'REMOVE'),
    ]
    medicine_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False)
    cart_id = serializers.IntegerField(required=False)
    action = serializers.ChoiceField(choices=CHOICES)


class AlternateMedicineSerializer(serializers.Serializer):
    medicine_id = serializers.IntegerField(required=False)
