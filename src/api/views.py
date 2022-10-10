import datetime
from copy import copy
from datetime import date

from dateutil import parser
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers, utils
from .models import Room, Category, Booking, BookingPayment
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


class BookingPaymentListView(generics.ListCreateAPIView):
    serializer_class = serializers.BookingPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_queryset(self):
        pk = self.kwargs["pk"]
        booking = get_object_or_404(Booking, pk=pk)
        return BookingPayment.objects.filter(booking=booking)


class BookingPaymentUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.BookingPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        booking = get_object_or_404(BookingPayment, pk=pk)
        return booking


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
        check_in_date = parser.parse(check_in_date, dayfirst=True)
        check_out_date = request.data['check_out_date']
        check_out_date = parser.parse(check_out_date, dayfirst=True)
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
            if utils.get_availability(check_in_date, check_out_date)[name] >= number_of_rooms:
                rooms = Room.objects.filter(category=room_category)[:number_of_rooms]
                for room in rooms:
                    rooms_.append(room)
            else:
                warnings.append(f"{name} exceeds availability, cannot create booking")
        booking.rooms.set(rooms_)
        booking.save()
        return Response(data={'message': 'Success!', 'warnings': warnings},
                        status=status.HTTP_200_OK)


class UpdateBookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, pk, format=None):
        booking = get_object_or_404(Booking, pk=pk)
        check_in_date = request.data['check_in_date']
        booking.check_in_date = parser.parse(check_in_date, dayfirst=True)
        check_out_date = request.data['check_out_date']
        booking.check_out_date = parser.parse(check_out_date, dayfirst=True)
        booking.customer_name = request.data['customer_name']
        booking.customer_phone = request.data['customer_phone']
        booking.customer_email = request.data['customer_email']
        booking.customer_cnic = request.data['customer_cnic']
        categories = request.data['categories']
        rooms_ = []
        warnings = []
        for category in categories:
            name = category['name']
            number_of_rooms = category['number_of_rooms']
            room_category = get_object_or_404(Category, name=name)
            x = utils.get_availability(booking.check_in_date, booking.check_out_date)
            if x[name] >= number_of_rooms:
                rooms = Room.objects.filter(category=room_category)[:number_of_rooms]
                for room in rooms:
                    rooms_.append(room)
            else:
                warnings.append(f"{name} exceeds availability, cannot create booking")
        booking.rooms.set(rooms_)
        booking.save()

        categories = Category.objects.all()
        dict_ = {}
        for category in categories:
            dict_[category.name] = booking.rooms.filter(category=category).count()
        booking_dict = {
            'pk': booking.pk,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'customer_name': booking.customer_name,
            'customer_phone': booking.customer_phone,
            'customer_email': booking.customer_email,
            'customer_cnic': booking.customer_cnic,
            'bookings': dict_,
        }

        return Response(data=booking_dict,
                        status=status.HTTP_200_OK)


class BookingGetAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, date_, format=None):
        date_ = parser.parse(date_, dayfirst=True)
        bookings = Booking.objects.filter(check_in_date__lte=date_, check_out_date__gte=date_)
        booking_array = []

        for booking in bookings:
            categories = Category.objects.all()
            dict_ = {}
            for category in categories:
                dict_[category.name] = booking.rooms.filter(category=category).count()
            booking_dict = {
                'pk': booking.pk,
                'check_in_date': booking.check_in_date,
                'check_out_date': booking.check_out_date,
                'customer_name': booking.customer_name,
                'customer_phone': booking.customer_phone,
                'customer_email': booking.customer_email,
                'customer_cnic': booking.customer_cnic,
                'bookings': dict_,
            }
            booking_array.append(booking_dict)

        return Response(data=booking_array,
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
        end_date = today + datetime.timedelta(days=1)
        rooms = utils.get_availability(today, end_date)
        return Response(data=rooms,
                        status=status.HTTP_200_OK)


class AvailabilityTargetDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, date_, end_date_, *args, **kwargs):
        target_date = parser.parse(date_, dayfirst=True)
        target_end_date = parser.parse(end_date_, dayfirst=True)
        rooms = utils.get_availability(target_date, target_end_date)
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
        context_bookings = []
        for booking in bookings:
            context_bookings.append(booking)
            temp_booking = copy(booking)
            initial_date = booking.check_in_date
            days_between = utils.days_between(initial_date, booking.check_out_date)
            for x in range(days_between):
                temp_booking.check_in_date = temp_booking.check_in_date + datetime.timedelta(days=1)
                new_temp = copy(temp_booking)
                context_bookings.append(new_temp)

        return Response(data=serializers.BookingSerializer(context_bookings, many=True).data,
                        status=status.HTTP_200_OK)


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
