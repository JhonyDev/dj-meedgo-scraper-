from datetime import date

from dateutil import parser
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers, utils
from .models import Room, Category, Booking
from ..accounts.authentication import JWTAuthentication
from ..accounts.models import User


class UsersListView(generics.ListCreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(type="Manager")

    def perform_create(self, serializer):
        user = serializer.save()
        user.type = "Manager"
        user.save()


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        if not self.request.user.is_superuser:
            raise utils.get_api_exception("You are not allowed to update users details", status.HTTP_403_FORBIDDEN)
        pk = self.kwargs["pk"]
        return get_object_or_404(User, pk=pk)


class RoomRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Room, pk=pk)


class RoomsListView(generics.ListCreateAPIView):
    serializer_class = serializers.RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Room.objects.all()


class CategoryRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Category, pk=pk)


class CategoryListView(generics.ListCreateAPIView):
    serializer_class = serializers.CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Category.objects.all()


class CategoryCreateView(generics.ListCreateAPIView):
    serializer_class = serializers.CategoryPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        categories = Category.objects.all()
        for category in categories:
            rooms = Room.objects.filter(category=category).count()
            category.number_of_rooms = rooms
        return categories

    def perform_create(self, serializer):
        category = serializer.save()
        for x in range(category.number_of_rooms):
            Room.objects.create(category=category)


class CategoryNumRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CategoryNumSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        category = get_object_or_404(Category, pk=pk)
        rooms = Room.objects.filter(category=category).count()
        category.number_of_rooms = rooms

        return category


class BookingRUV(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Booking, pk=pk, manager=self.request.user)


class BookingListView(generics.ListCreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Booking.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        booking = serializer.save(manager=self.request.user)
        bookings = Booking.objects.filter(check_in_date__gte=booking.check_in_date,
                                          check_out_date__lt=booking.check_in_date)
        if bookings.exists():
            booking.delete()
            raise ValidationError('Booking cannot be created, check in date conflicts with another booking')

        bookings = Booking.objects.filter(check_in_date__gt=booking.check_out_date,
                                          check_out_date__lte=booking.check_out_date)
        if bookings.exists():
            booking.delete()
            raise ValidationError('Booking cannot be created, check out date conflicts with another booking')


class BookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        check_in_date = request.data['check_in_date']
        check_in_date = parser.parse(check_in_date)
        check_out_date = request.data['check_out_date']
        check_out_date = parser.parse(check_out_date)
        customer_name = request.data['customer_name']
        customer_phone = request.data['customer_phone']
        customer_email = request.data['customer_email']
        customer_cnic = request.data['customer_cnic']
        categories = request.data['categories']
        booking = Booking.objects.create(check_out_date=check_out_date, check_in_date=check_in_date,
                                         customer_name=customer_name, customer_phone=customer_phone,
                                         customer_email=customer_email, customer_cnic=customer_cnic)

        rooms_ = []
        warnings = []
        for category in categories:
            name = category['name']
            number_of_rooms = category['number_of_rooms']
            room_category = get_object_or_404(Category, name=name)
            if utils.get_availability(check_in_date)[name] >= number_of_rooms:
                rooms = Room.objects.filter(category=room_category)[:number_of_rooms]
                for room in rooms:
                    rooms_.append(room)
            else:
                warnings.append(f"{name} exceeds availability, cannot create booking")
        booking.rooms.set(rooms_)
        booking.save()
        return Response(data={'message': 'Success!', 'warnings': warnings},
                        status=status.HTTP_200_OK)


class BookingRUVGeneral(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Booking, pk=pk)


class BookingListViewGeneral(generics.ListCreateAPIView):
    serializer_class = serializers.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Booking.objects.all()


class AvailabilityToday(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = date.today()
        rooms = utils.get_availability(today)
        return Response(data=rooms,
                        status=status.HTTP_200_OK)


class AvailabilityTargetDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, date_, *args, **kwargs):
        target_date = parser.parse(date_)
        rooms = utils.get_availability(target_date)
        return Response(data=rooms,
                        status=status.HTTP_200_OK)


class BookingsMonth(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, month, year, *args, **kwargs):
        target_start_date, target_end_date = utils.get_target_dates(month, year)
        bookings = Booking.objects.filter(created_on__lte=target_end_date, created_on__gte=target_start_date,
                                          manager=self.request.user)
        return Response(data=serializers.BookingSerializer(bookings, many=True).data,
                        status=status.HTTP_200_OK)


class BookingsMonthGeneral(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, month, year, *args, **kwargs):
        target_start_date, target_end_date = utils.get_target_dates(month, year)
        bookings = Booking.objects.filter(check_in_date__lte=target_end_date, check_in_date__gte=target_start_date)
        return Response(data=serializers.BookingSerializer(bookings, many=True).data,
                        status=status.HTTP_406_NOT_ACCEPTABLE)


"""
{
   "check_in_date":"2022-10-02",
   "check_out_date":"2022-10-02",
   "customer_name":"Junaid Khan",
   "customer_phone":"03345529803",
   "customer_email":"junaid@gmail.com",
   "customer_cnic":"7584854785858",
   "categories":[
      {
         "name":"Delux",
         "number_of_rooms":5
      },
      {
         "name":"PentHouse",
         "number_of_rooms":7
      },
      {
         "name":"Another",
         "number_of_rooms":10
      }
   ]
}
"""
