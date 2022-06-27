from rest_framework import permissions, generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions as cp
from . import serializers
from . import utils
from .models import Clinic, Slot, Appointment
from ..accounts.models import User


class PostRegistrationFormView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserDetailsSerializer

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise utils.get_api_exception(str(e), status.HTTP_409_CONFLICT)


class UserDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user


""" SUB-ADMIN + SUPER-ADMIN APIS """


class MyManagersView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,
                          cp.SubAdminPermission | cp.SuperAdminPermission]
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        return User.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, type='Manager')


class ManagerView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,
                          cp.SubAdminPermission | cp.SuperAdminPermission]
    serializer_class = serializers.UserSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(User, pk=pk, creator=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MyClinicsView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated,
                          cp.SubAdminPermission | cp.SuperAdminPermission]
    serializer_class = serializers.ClinicSerializer

    def get_queryset(self):
        return Clinic.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user)


""" MANAGER + SUB-ADMIN APIS + SUPER-ADMIN APIS """


class ClinicView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,
                          cp.SuperAdminPermission | cp.ManagerPermission]
    serializer_class = serializers.ClinicSerializer

    def get_object(self):
        return get_object_or_404(Clinic, manager=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


""" MANAGER APIS """


class SlotsView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.ManagerPermission | cp.SuperAdminPermission]
    serializer_class = serializers.SlotSerializer

    def get_queryset(self):
        return Slot.objects.filter(clinic__manager=self.request.user)

    def perform_create(self, serializer):
        clinic = get_object_or_404(Clinic, manager=self.request.user)
        serializer.save(clinic=clinic)


class SlotView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.ManagerPermission | cp.SuperAdminPermission]
    serializer_class = serializers.SlotSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Slot, pk=pk, clinic__manager=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ClinicAppointmentsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.ManagerPermission | cp.SuperAdminPermission]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        clinic = get_object_or_404(Clinic, manager=self.request.user)
        return Appointment.objects.filter(slot__clinic=clinic)


class UpdateAppointmentStatus(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.ManagerPermission | cp.SuperAdminPermission]
    serializer_class = serializers.ManagerAppointmentSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs['pk']
        clinic = get_object_or_404(Clinic, manager=self.request.user)
        return get_object_or_404(Appointment, pk=pk, slot__clinic=clinic)


""" PATIENT APIS """


class CustomerAppointmentView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.PatientPermission | cp.SuperAdminPermission]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentHistory(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, cp.PatientPermission | cp.SuperAdminPermission]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user, status='Complete')


class CreateAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, cp.PatientPermission | cp.SuperAdminPermission]

    def get(self, request, *args, **kwargs):
        appointments = Appointment.objects.filter(patient=self.request.user)
        serializer = serializers.AppointmentSerializer(appointments, many=True).data
        return Response(data=serializer,
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        slot_pk = kwargs['pk']
        slot = Slot.objects.get(pk=slot_pk)
        total_appointments_in_slot = Appointment.objects.filter(slot=slot).count()
        if total_appointments_in_slot >= slot.number_of_appointments:
            raise utils.get_api_exception("Slot full, Further appointments cannot be created",
                                          status.HTTP_406_NOT_ACCEPTABLE)
        appointment = Appointment.objects.create(patient=request.user, slot=slot)
        serializer = serializers.AppointmentSerializer(appointment, many=False).data
        return Response(data=serializer, status=status.HTTP_201_CREATED)
