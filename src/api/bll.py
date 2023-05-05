from collections import defaultdict

from rest_framework import status
from rest_framework.response import Response

from src.api.models import Medicine, MedicineCartBridge
from src.api.models import MedicineCart
from src.api.serializers import MedicineCartSerializer
from src.api.utils import LIST_PLATFORMS, get_platform_dict


def add_medicine_to_card(self, request):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    cart_id = serializer.validated_data.get('cart_id')
    medicine_id = serializer.validated_data.get('medicine_id')
    if medicine_id is None and cart_id is None:
        return Response({'error': 'Provide "cart_id" to get Cart Data '
                                  'or Provide "medicine_id" to create new cart and add medicine'},
                        status=status.HTTP_400_BAD_REQUEST)
    if cart_id:
        try:
            cart = MedicineCart.objects.get(id=cart_id)
        except MedicineCart.DoesNotExist:
            return Response({'error': 'Cart does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        cart = MedicineCart.objects.create()
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        MedicineCartBridge.objects.create(medicine=medicine, medicine_card=cart)
    except Medicine.DoesNotExist:
        pass
    cart_serialized = MedicineCartSerializer(cart)
    medicines = cart.medicines.all()
    medicines_by_platform = defaultdict(list)
    for medicine in medicines:
        medicines_by_platform[medicine.platform].append(medicine)

    platforms_list = []
    for platform in LIST_PLATFORMS:
        platform_medicines = Medicine.objects.filter(platform=get_platform_dict()[platform])
        missing_count = 0
        total_cost = 0
        for medicine in cart.medicines.all():
            query_set = platform_medicines.filter(
                name=medicine.name, salt_name=medicine.salt_name, dosage=medicine.dosage)
            if not query_set.exists():
                missing_count += 1
            else:
                total_cost += query_set.first().price or 0
        platforms_list.append(
            {'platform': platform, 'total_cost': total_cost, 'status': f'{missing_count} medicines are missing'})
    return Response({'cart_id': cart.id,
                     'cost_comparisons': platforms_list,
                     'medicines': cart_serialized.data['medicines']},
                    status=status.HTTP_201_CREATED)
