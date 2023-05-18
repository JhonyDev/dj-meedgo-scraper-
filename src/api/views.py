from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart, OrderRequest
from .serializers import MedicineSerializer, MedicineToCartSerializer, \
    OrderRequestListSerializer, OrderRequestCreateSerializer
from .tasks import update_medicine, scrape_netmeds, scrape_pharmeasy, update_medicine_pharmeasy, scrape_1mg, \
    update_medicine_1mg
from .utils import get_platform_dict, NET_MEDS, PHARM_EASY, ONE_MG


class MedicineSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Medicine.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_backends = [SearchFilter]
    # search_fields = ['name', 'salt_name']
    serializer_class = MedicineSerializer

    def get_queryset(self):
        param = self.request.query_params.get('search')
        queryset = Medicine.objects.all()
        if param:
            queryset = queryset.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
            if not queryset.exists():
                med_list = scrape_pharmeasy(param)
                queryset = Medicine.objects.filter(pk__in=med_list)
                # if not Medicine.objects.filter(Q(name__icontains=param) | Q(salt_name__icontains=param)).exists():
                #     scrape_netmeds(param)
            scrape_pharmeasy.delay(param)
            scrape_1mg.delay(param)
            scrape_netmeds.delay(param)
        for med in queryset:
            if not med.salt_name and med.med_url:
                if med.platform == get_platform_dict()[PHARM_EASY]:
                    update_medicine_pharmeasy.delay(med.pk)
                if med.platform == get_platform_dict()[NET_MEDS]:
                    update_medicine.delay(med.pk)
                if med.platform == get_platform_dict()[ONE_MG]:
                    update_medicine_1mg.delay(med.pk)

        # print(queryset)
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


class OrderRequestsView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderRequestListSerializer
        elif self.request.method == 'POST':
            return OrderRequestCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return OrderRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()
