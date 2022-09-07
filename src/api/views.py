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
        return User.objects.all()


class UserDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
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

    def get(self, request, date, *args, **kwargs):
        today = date.today()
        rooms = utils.get_availability(today)
        return Response(data=serializers.RoomSerializer(rooms, many=True).data,
                        status=status.HTTP_200_OK)


class AvailabilityTargetDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, date, *args, **kwargs):
        target_date = parser.parse(date)
        rooms = utils.get_availability(target_date)
        return Response(data=serializers.RoomSerializer(rooms, many=True).data,
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
        bookings = Booking.objects.filter(created_on__lte=target_end_date, created_on__gte=target_start_date)
        return Response(data=serializers.BookingSerializer(bookings, many=True).data,
                        status=status.HTTP_200_OK)
