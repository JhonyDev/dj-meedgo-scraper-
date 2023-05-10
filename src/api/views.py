from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart
from .serializers import MedicineSerializer, MedicineToCartSerializer
from .tasks import update_medicine, scrape_netmeds, scrape_pharmeasy, update_medicine_pharmeasy
from .utils import get_platform_dict, NET_MEDS, PHARM_EASY


class MedicineSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Medicine.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_backends = [SearchFilter]
    # search_fields = ['name', 'salt_name']
    serializer_class = MedicineSerializer

    def get_queryset(self):
        queryset = Medicine.objects.all()
        param = self.request.query_params.get('search')
        if param:
            if not Medicine.objects.filter(Q(name__icontains=param) | Q(salt_name__icontains=param)).exists():
                med_list = scrape_pharmeasy(param)
                print(med_list)
                queryset = Medicine.objects.filter(pk__in=med_list)
                # if not Medicine.objects.filter(Q(name__icontains=param) | Q(salt_name__icontains=param)).exists():
                #     scrape_netmeds(param)
            scrape_pharmeasy.delay(param)
            scrape_netmeds.delay(param)
            if not queryset.exists():
                queryset = Medicine.objects.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
        for med in queryset:
            if not med.salt_name and not med.price and med.med_url:
                if med.platform == get_platform_dict()[PHARM_EASY]:
                    update_medicine_pharmeasy.delay(med.pk)
                if med.platform == get_platform_dict()[NET_MEDS]:
                    update_medicine.delay(med.pk)
        print(queryset)
        return queryset


class MedicineToCartView(generics.GenericAPIView):
    serializer_class = MedicineToCartSerializer
    queryset = MedicineCart.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({'message': 'Please use POST Method. Provide "cart_id" to get Cart Data '
                                    'or Provide "medicine_id" to create new cart and add medicine'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        return add_medicine_to_card(self, request)


class AlternateMedicineView(generics.ListAPIView):
    serializer_class = MedicineSerializer
    queryset = Medicine.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        target_medicine = get_object_or_404(Medicine, pk=self.kwargs.get('medicine_pk'))
        if not target_medicine.salt_name:
            return Medicine.objects.none()
        return Medicine.objects.filter(
            salt_name=target_medicine.salt_name).order_by('price')
