from django.db.models import Sum
from rest_framework import serializers

from src.accounts.models import User, LicenseEntry
from .models import Medicine, MedicineCart, OrderRequest, GrabUserBridge, MedicineOfferBridge, MedicineCartBridge, \
    ConversationHistory, Message, UserRating


class UserGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username', 'full_name', 'email', 'postal_code', 'profile_image')


class UserProfileSerializer(serializers.ModelSerializer):
    is_documentation_complete = serializers.SerializerMethodField('get_documentation')

    def get_documentation(self, obj):
        return LicenseEntry.objects.filter(user=obj).exists() \
               and obj.pan_card_image is not None \
               and obj.store_photo is not None \
               and obj.profile_image is not None \
               and obj.type_of_ownership is not None \
               and obj.pan_number is not None \
               and obj.business_name is not None \
               and obj.aadhar_card is not None

    class Meta:
        model = User
        exclude = (
            'is_store_photo_approved',
            'is_aadhar_card_approved',
            'is_pan_card_approved',
            'otp_secret',
            'otp_created',
            'otp_sent',
            'password', 'first_name', 'last_name', 'type', 'date_joined', 'username', 'groups', 'is_superuser',
            'is_active', 'user_permissions')


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User(
            full_name=self.validated_data['full_name'],
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.full_name = validated_data['full_name']
        instance.email = validated_data['email']
        instance.username = validated_data['username']
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            'pk', 'full_name', 'username', 'email', 'phone_number',
            'is_staff', 'postal_code', 'password'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }

        read_only_fields = [
            'date_joined', 'type', 'is_superuser', 'is_staff', 'user_password'
        ]


class MedicineSerializer(serializers.ModelSerializer):
    platform = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField('get_price')

    def get_price(self, obj):
        return obj.price if obj.price is not None else obj.discounted_price

    class Meta:
        model = Medicine
        fields = ['pk', 'name', 'salt_name', 'price', 'discounted_price', 'med_image', 'med_url', 'platform',
                  'is_available']

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
        fields = ['pk', 'medicine_cart', 'order_status']


class OrderRequestCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = ['pk', 'order_status']


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
        fields = ['is_active', 'is_accepted']


class MedicineOfferSerializer(serializers.ModelSerializer):
    medicine_cart_bridge = MedicineCartBridgeSerializer()

    class Meta:
        model = MedicineOfferBridge
        fields = ['pk', 'offered_price', 'medicine_cart_bridge']


class MedicineOfferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineOfferBridge
        fields = ['offered_price']


class GrabbedOrderRequestsListSerializer(serializers.ModelSerializer):
    # order_request = OrderRequestListSerializer()
    medicine_offers = serializers.SerializerMethodField('get_medicine_offers')
    offered_total_price = serializers.SerializerMethodField('get_offered_total')
    cost_comparisons = serializers.SerializerMethodField('get_cost_comparisons')
    customer = serializers.SerializerMethodField('get_customer')

    def get_customer(self, q):
        return UserGeneralSerializer(q.order_request.user, many=False).data

    def get_cost_comparisons(self, q):
        from core.settings import LIST_PLATFORMS
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
                'status': f'{missing_count} products are missing'
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
        fields = ['pk', 'customer', 'order_request', 'cost_comparisons', 'medicine_offers', 'offered_total_price',
                  'is_active']

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


class ConversationHistoryListSerializer(serializers.ModelSerializer):
    target_user = UserGeneralSerializer()
    last_message = serializers.SerializerMethodField('get_last_message')

    def get_last_message(self, q):
        last_message = Message.objects.filter(conversation_history=q).order_by('-pk').first()
        return MessageGeneralSerializer(last_message, many=False).data

    class Meta:
        model = ConversationHistory
        fields = ['pk', 'target_user', 'last_message']


class ConversationHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationHistory
        fields = '__all__'


class MessageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message', 'created_on', 'author')


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('author', 'conversation_history')


class MessageGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message', 'created_on')


class UserRatingListSerializer(serializers.ModelSerializer):
    given_to = UserGeneralSerializer()

    class Meta:
        model = UserRating
        exclude = ('given_by',)


class UserRatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        exclude = ('given_by',)
