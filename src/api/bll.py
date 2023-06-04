from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response

from core.settings import LIST_PLATFORMS
from src.api.models import Medicine, MedicineCartBridge
from src.api.models import MedicineCart
from src.api.serializers import MedicineCartSerializer
from src.api.utils import get_platform_dict
from .utils import get_api_exception, get_similarity_queryset


def add_medicine_to_card(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    quantity = serializer.validated_data.get('quantity')
    action = serializer.validated_data.get('action')
    cart_id = serializer.validated_data.get('cart_id')
    medicine_id = serializer.validated_data.get('medicine_id')
    if medicine_id is None and cart_id is None:
        return Response(
            {'error': 'Provide "cart_id" to get Cart Data '
                      'or Provide "medicine_id" to create new cart and add medicine'
             }, status=status.HTTP_400_BAD_REQUEST)
    if cart_id:
        try:
            cart = MedicineCart.objects.get(id=cart_id)
        except MedicineCart.DoesNotExist:
            raise get_api_exception('Cart does not exist.', status.HTTP_400_BAD_REQUEST)

    else:
        cart = MedicineCart.objects.create()
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        target_med_bridge = MedicineCartBridge.objects.filter(medicine=medicine, medicine_card=cart)
        if action == 'ADD':
            if target_med_bridge.exists():
                target_med_bridge = target_med_bridge.first()
                target_med_bridge.quantity = quantity or target_med_bridge.quantity
                target_med_bridge.save()
            else:
                MedicineCartBridge.objects.create(medicine=medicine, medicine_card=cart)
        if action == 'REMOVE':
            target_med_bridge.delete()

    except Medicine.DoesNotExist:
        pass
    cart_serialized = MedicineCartSerializer(cart)
    medicines = cart.medicines.all()
    medicines_by_platform = defaultdict(list)
    for medicine in medicines:
        medicines_by_platform[medicine.platform].append(medicine)
    platforms_list = []
    for platform in LIST_PLATFORMS:
        missing_count = 0
        total_cost = 0
        for medicine in cart.medicines.all():
            print(f'{"=" * 15} CHECKING FOR {medicine.name} - {medicine.salt_name} {"=" * 15}')
            print(f'{"-" * 15} PLATFORM - {platform}')
            # query_set = platform_medicines.filter(salt_name__icontains=medicine.salt_name)
            platform_medicines = Medicine.objects.filter(platform=get_platform_dict()[platform], price=medicine.price)
            print(f'{"-" * 15} Platform - {get_platform_dict()[platform]}')
            print(f'{"-" * 15} Medicine Price - {medicine.price}')
            print(f'{"-" * 15} Medicines - {platform_medicines}')
            query_set = get_similarity_queryset(
                platform_medicines, medicine.name, medicine.salt_name, True)
            if not query_set.exists():
                missing_count += 1
            else:
                total_cost += query_set.first().discounted_price or query_set.first().price or 0

        platforms_list.append({
            'platform': platform,
            'total_cost': round(total_cost, 2),
            'status': f'{missing_count} medicines are missing'
        })

    response_context = {
        'cart_id': cart.id,
        'cost_comparisons': platforms_list,
        'medicines': cart_serialized.data['medicines']
    }
    return Response(response_context, status=status.HTTP_201_CREATED)
