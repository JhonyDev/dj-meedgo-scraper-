from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart
from .serializers import MedicineSerializer, MedicineToCartSerializer


class MedicineSearchView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'salt_name']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10


class MedicineToCartView(generics.GenericAPIView):
    serializer_class = MedicineToCartSerializer
    queryset = MedicineCart.objects.all()
    permission_classes = [permissions.AllowAny]

    # def get(self, request):
    #     return Response({'message': 'Please use POST Method. Provide "cart_id" to get Cart Data '
    #                                 'or Provide "medicine_id" to create new cart and add medicine'},
    #                     status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        return add_medicine_to_card(self, request)
