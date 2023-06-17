from django.db.models import Sum, Q, F, OuterRef, Subquery
from django.shortcuts import redirect, render
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from core.consumers import send_message_to_group
from core.settings import PHARM_EASY, NET_MEDS, ONE_MG, FIRST_MESSAGE_WHEN_ORDER_ACCEPTED
from . import utils
from .bll import add_medicine_to_card
from .models import Medicine, MedicineCart, OrderRequest, GrabUserBridge, MedicineOfferBridge, ConversationHistory, \
    Message, UserRating
from .serializers import MedicineSerializer, MedicineToCartSerializer, \
    OrderRequestListSerializer, OrderRequestCreateSerializer, GrabbedOrderRequestsListSerializer, \
    GrabbedOrderRequestsCreateSerializer, GrabbedOrderRequestsUpdateSerializer, MedicineOfferSerializer, \
    MedicineOfferUpdateSerializer, LocalityOrderRequestListSerializer, \
    ConversationHistoryListSerializer, ConversationHistoryCreateSerializer, MessageCreateSerializer, \
    MessageListSerializer, UserRatingListSerializer, UserRatingCreateSerializer, OrderRequestCompleteSerializer
from .tasks import scrape_pharmeasy, update_medicine_pharmeasy, update_medicine, \
    update_medicine_1mg
from .utils import get_platform_dict, balance_medicines
from ..accounts.authentication import JWTAuthentication

"""ADMIN-TASKS"""


def custom_method_view(request, object_id):
    # import csv
    # with open('med_names.csv', 'r') as file:
    #     csv_reader = csv.reader(file)
    #     for row in csv_reader:
    #         for value in row:
    #             # scrape_1mg.delay(value)
    #             # scrape_flipkart.delay(value)
    #             # scrape_netmeds.delay(value)
    #             scrape_pharmeasy.delay(value)

    med = Medicine.objects.get(pk=object_id)
    if med.platform == get_platform_dict()[PHARM_EASY]:
        update_medicine_pharmeasy(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[NET_MEDS]:
        all_meds = Medicine.objects.filter(platform=get_platform_dict()[NET_MEDS], salt_name=None,
                                           price=None, discounted_price=None).values_list('pk', flat=True)
        for med_ in all_meds:
            update_medicine.delay(med_, is_forced=True)
        update_medicine(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[ONE_MG]:
        update_medicine_1mg(med.pk, is_forced=True)
    return redirect('admin:api_medicine_change', object_id)


def custom_method_all_view(request, object_id):
    med = Medicine.objects.get(pk=object_id)
    queryset = Medicine.objects.filter(
        Q(name='') |
        Q(salt_name__isnull=True) |
        Q(price__isnull=True) |
        Q(discounted_price__isnull=True) |
        Q(price=F('discounted_price'))
    )
    if med.platform == get_platform_dict()[PHARM_EASY]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[PHARM_EASY]).values_list('pk', flat=True):
            update_medicine_pharmeasy.delay(med_, is_forced=True)
        update_medicine_pharmeasy(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[NET_MEDS]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[NET_MEDS]).values_list('pk', flat=True):
            update_medicine.delay(med_, is_forced=True)
        update_medicine(med.pk, is_forced=True)
    if med.platform == get_platform_dict()[ONE_MG]:
        for med_ in queryset.filter(
                platform=get_platform_dict()[ONE_MG]).values_list('pk', flat=True):
            update_medicine_1mg.delay(med_, is_forced=True)
        update_medicine_1mg(med.pk, is_forced=True)
    return redirect('admin:api_medicine_change', object_id)


def lobby(request):
    Medicine.objects.filter(salt_name=None, price=None, discounted_price=None, name='').delete()
    return render(request, 'api/lobby.html')


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


class UserRatingViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserRating.objects.all()
    serializer_class = UserRatingListSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserRatingListSerializer
        elif self.request.method == 'POST':
            return UserRatingCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(given_by=self.request.user)

    def get_queryset(self):
        return UserRating.objects.filter(given_by=self.request.user)


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
        orig_queryset = Medicine.objects.exclude(price=None, discounted_price=None)
        if param is None:
            return orig_queryset
        # queryset = orig_queryset.filter(Q(name__icontains=param) | Q(salt_name__icontains=param))
        queryset = None

        # scrape_flipkart.delay(param)
        # scrape_netmeds.delay(param)
        # scrape_pharmeasy.delay(param)
        # scrape_1mg.delay(param)

        # queryset = param_contains_name.union(param_contains_salt, all=True).union(queryset, all=True)
        # for med in queryset:
        #     if not med.salt_name and med.med_url:
        #         if med.platform == get_platform_dict()[PHARM_EASY]:
        #             update_medicine_pharmeasy.delay(med.pk)
        #         if med.platform == get_platform_dict()[NET_MEDS]:
        #             update_medicine.delay(med.pk)
        #         if med.platform == get_platform_dict()[ONE_MG]:
        #             update_medicine_1mg.delay(med.pk)
        if param and not queryset:
            queryset = utils.get_similarity_queryset(orig_queryset, param)
            print(queryset)
            if not queryset:
                med_list = scrape_pharmeasy(param)
                queryset = Medicine.objects.filter(pk__in=med_list)
        return queryset


class MedicineToCartView(generics.GenericAPIView):
    serializer_class = MedicineToCartSerializer
    authentication_classes = [JWTAuthentication]
    queryset = MedicineCart.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # send_message_to_group('15100', "CHECKING MESSAGE")
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
        query_set = Medicine.objects.filter(salt_name=target_medicine.salt_name)
        query_set = query_set.exclude(salt_name=None)
        if not query_set.exists():
            query_set = Medicine.objects.filter(pk=target_medicine.pk)
        return query_set.order_by('price')


class OrderRequestUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderRequestCompleteSerializer
    queryset = OrderRequest.objects.all()


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
        return OrderRequest.objects.filter(user=self.request.user).order_by('-pk')

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()
        order_request = {
            'total_medicines': instance.medicine_cart.medicines.all().count(),
            'total_price': instance.medicine_cart.medicines.aggregate(total=Sum('price'))['total'],
            'order_id': instance.id,
            'chemist_id': instance.user.pk
        }
        send_message_to_group(f'{self.request.user.postal_code}', order_request)
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        return Response(OrderRequestListSerializer(instance, many=False).data,
                        status=status.HTTP_201_CREATED)


class OrderRequestsLocalityView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocalityOrderRequestListSerializer

    def get_queryset(self):
        if self.request.GET.get('scope') == 'missed':
            grabs = GrabUserBridge.objects.filter(user=self.request.user).values_list('order_request__pk', flat=True)
            return OrderRequest.objects.filter(user__postal_code=self.request.user.postal_code).exclude(pk__in=grabs)
        return OrderRequest.objects.filter(user__postal_code=self.request.user.postal_code)


class GrabOrdersView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

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
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        return Response(GrabbedOrderRequestsListSerializer(instance, many=False).data,
                        status=status.HTTP_201_CREATED)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        for grab_user_bridge in GrabUserBridge.objects.filter(user=self.request.user):
            balance_medicines(grab_user_bridge)


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

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.is_active:
            data = GrabbedOrderRequestsListSerializer(instance).data
            send_message_to_group(f'order-request-{instance.order_request.pk}', data)

        if instance.is_accepted:
            chemist = instance.user
            instance.order_request.status = 'Picked'
            instance.order_request.save()
            customer = self.request.user
            conversation_history = ConversationHistory.objects.filter(
                Q(sending_user=customer, receiving_user=chemist) | Q(receiving_user=customer, sending_user=chemist))
            if conversation_history.exists():
                conversation_history = conversation_history.first()
            else:
                conversation_history = ConversationHistory.objects.create(
                    sending_user=customer, receiving_user=chemist)
            message = Message.objects.create(
                conversation_history=conversation_history, author=self.request.user,
                message=FIRST_MESSAGE_WHEN_ORDER_ACCEPTED)
            send_message_to_group(f'receiver-{customer.pk}', MessageListSerializer(message, many=False).data)
            send_message_to_group(f'receiver-{chemist.pk}', MessageListSerializer(message, many=False).data)


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


class ConversationHistoryListView(generics.ListCreateAPIView):
    serializer_class = ConversationHistoryListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ConversationHistoryListSerializer
        elif self.request.method == 'POST':
            return ConversationHistoryCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        last_message_subquery = Message.objects.filter(conversation_history=OuterRef('pk')).order_by('-pk')
        conversations = ConversationHistory.objects.filter(
            Q(sending_user=self.request.user) | Q(receiving_user=self.request.user)).annotate(
            created_on=Subquery(last_message_subquery.values('created_on')[:1])
        ).order_by('-created_on')
        for conversation in conversations:
            conversation.target_user = conversation.get_target_user(self.request.user)
        return conversations


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageListSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MessageListSerializer
        elif self.request.method == 'POST':
            return MessageCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return Message.objects.filter(conversation_history__pk=self.kwargs.get('pk')).order_by('-pk')

    def perform_create(self, serializer):
        conversation_history = ConversationHistory.objects.get(pk=self.kwargs.get('pk'))
        instance = serializer.save()
        instance.author = self.request.user
        instance.conversation_history = conversation_history
        instance.save()
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        send_message_to_group(f'receiving-{instance.conversation_history.get_target_user(self.request.user).pk}',
                              MessageListSerializer(instance, many=False).data)
        send_message_to_group(f'receiving-{self.request.user.pk}',
                              MessageListSerializer(instance, many=False).data)

        print("SENDING MESSAGE TO FOLLOWING GROUPS")
        print(
            f'receiving-{instance.conversation_history.get_target_user(self.request.user).pk} :: {MessageListSerializer(instance, many=False).data}')
        print(
            f'receiving-{self.request.user.pk} :: {MessageListSerializer(instance, many=False).data}')

        return Response(MessageListSerializer(self.get_queryset(), many=True).data,
                        status=status.HTTP_201_CREATED)


class UserRatingListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    queryset = UserRating.objects.all()
    serializer_class = UserRatingListSerializer

    def get_queryset(self):
        return UserRating.objects.filter(pharmacist=self.request.user).order_by('-pk')
