from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart
from .serializers import MedicineSerializer, MedicineToCartSerializer
from .tasks import scrape_netmeds, update_medicine


class MedicineSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Medicine.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_backends = [SearchFilter]
    search_fields = ['name', 'salt_name']
    serializer_class = MedicineSerializer

    def get_queryset(self):
        queryset = Medicine.objects.all()
        param = self.request.query_params.get('search')
        if param:
            queryset = queryset.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
            if not queryset.exists():
                scrape_netmeds(param)
                queryset = queryset.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
            else:
                scrape_netmeds.delay(param)

        for med in queryset:
            if not med.name and not med.salt_name and not med.price and med.med_url:
                update_medicine.delay(med.pk)
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
        return Medicine.objects.filter(
            salt_name=target_medicine.salt_name).exclude(pk=target_medicine.pk).order_by('price')[:1]
