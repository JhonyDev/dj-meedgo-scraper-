from fuzzywuzzy import fuzz
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart, OrderRequest, GrabUserBridge, MedicineOfferBridge
from .serializers import MedicineSerializer, MedicineToCartSerializer, \
    OrderRequestListSerializer, OrderRequestCreateSerializer, GrabbedOrderRequestsListSerializer, \
    GrabbedOrderRequestsCreateSerializer, GrabbedOrderRequestsUpdateSerializer, MedicineOfferSerializer, \
    MedicineOfferUpdateSerializer
from .tasks import scrape_pharmeasy, update_medicine_pharmeasy, scrape_1mg, scrape_netmeds, update_medicine, \
    update_medicine_1mg
from .utils import get_platform_dict, PHARM_EASY, balance_medicines, NET_MEDS, ONE_MG
from ..accounts.authentication import JWTAuthentication

"""
Elastic Search DSL (Domain Specific Language)

Query Annotations
    - Basic Annotation
    - Conditional Annotation
    - Related Model Annotation
    - Window Function Annotations

Atomic Transactions

ACID properties
    - Atomicity
    - Consistency
    - Isolation
    - Durability
"""


class MedicineSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]
    queryset = Medicine.objects.all()
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    filter_backends = [SearchFilter]
    serializer_class = MedicineSerializer

    def get_queryset(self):
        param = self.request.query_params.get('search')
        queryset = Medicine.objects.all()
        if param:
            similar_words = Medicine.objects.all().values('pk', 'name')
            similar_words = [word['pk'] for word in similar_words if fuzz.ratio(param, word['name']) > 65]
            # queryset = queryset.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
            queryset = queryset.filter(pk__in=similar_words)
            if not queryset:
                med_list = scrape_pharmeasy(param)
                queryset = Medicine.objects.filter(pk__in=med_list)
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
        return queryset


class MedicineToCartView(generics.GenericAPIView):
    serializer_class = MedicineToCartSerializer
    authentication_classes = [JWTAuthentication]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        target_medicine = get_object_or_404(Medicine, pk=self.kwargs.get('medicine_pk'))
        if not target_medicine.salt_name:
            return Medicine.objects.none()
        query_set = Medicine.objects.filter(
            salt_name=target_medicine.salt_name).order_by('price')
        if not query_set:
            query_set = Medicine.objects.filter(name=target_medicine.name)
        return query_set


class OrderRequestsView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
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


class OrderRequestsLocalityView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderRequestListSerializer

    def get_queryset(self):
        return OrderRequest.objects.filter(user__postal_code=self.request.user.postal_code)


class GrabOrdersView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for medicine in self.get_queryset():
            balance_medicines(medicine)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GrabbedOrderRequestsListSerializer
        elif self.request.method == 'POST':
            return GrabbedOrderRequestsCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return GrabUserBridge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()


class GrabOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = GrabUserBridge.objects.all()
    serializer_class = GrabbedOrderRequestsUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GrabbedOrderRequestsListSerializer
        elif self.request.method == 'UPDATE':
            return GrabbedOrderRequestsUpdateSerializer
        return super().get_serializer_class()

    def dispatch(self, request, *args, **kwargs):
        balance_medicines(self.get_object())
        return super().dispatch(request, *args, **kwargs)


class MedicineOfferUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = MedicineOfferBridge.objects.all()
    serializer_class = MedicineOfferUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MedicineOfferSerializer
        elif self.request.method == 'UPDATE':
            return MedicineOfferUpdateSerializer
        return super().get_serializer_class()
