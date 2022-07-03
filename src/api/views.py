from allauth.account.models import EmailAddress
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions as cp
from . import serializers
from . import utils
from .models import Clinic, Slot, Appointment, UserDetail
from ..accounts.authentication import JWTAuthentication
from ..accounts.models import User
from ..accounts.serializers import CustomRegisterAccountSerializer


class PostRegistrationFormView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.UserDetailsSerializer
    queryset = UserDetail.objects.all()

    def perform_create(self, serializer):
        print("Creating form data")
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise utils.get_api_exception(str(e), status.HTTP_409_CONFLICT)


class UserDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


""" SUB-ADMIN + SUPER-ADMIN APIS """


class MyManagersView(generics.ListCreateAPIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [cp.SubAdminPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return User.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        user = serializer.save()
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        user.creator = self.request.user
        user.type = 'Manager'
        user.save()


class ManagerView(generics.RetrieveUpdateAPIView):
    permission_classes = [
        cp.SubAdminPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.UserSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(User, pk=pk, creator=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class MyClinicsView(generics.ListCreateAPIView):
    permission_classes = [cp.SubAdminPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ClinicAdminSerializer

    def get_queryset(self):
        return Clinic.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            manager = serializer.validated_data['manager']
            try:
                User.objects.get(username=manager, creator=self.request.user)
            except User.DoesNotExist:
                raise utils.get_api_exception(
                    "Requested manager cannot be associated with the clinic, since you have not created this manager",
                    status.HTTP_403_FORBIDDEN)
            serializer.save(creator=self.request.user)
        else:
            raise utils.get_api_exception(serializer.errors, status.HTTP_400_BAD_REQUEST)


class MyClinicRUView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [cp.SubAdminPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ClinicAdminSerializer

    def get_object(self):
        return get_object_or_404(Clinic, pk=self.kwargs['pk'], creator=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


""" MANAGER + SUB-ADMIN APIS + SUPER-ADMIN APIS """


class ClinicView(generics.RetrieveUpdateAPIView):
    permission_classes = [cp.SuperAdminPermission | cp.ManagerPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ClinicManagerSerializer

    def get_object(self):
        return get_object_or_404(Clinic, manager=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


""" MANAGER APIS """


class SlotsView(generics.ListCreateAPIView):
    permission_classes = [cp.ManagerPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.SlotSerializer

    def get_queryset(self):
        return Slot.objects.filter(clinic__manager=self.request.user)

    def perform_create(self, serializer):
        try:
            clinic = Clinic.objects.get(manager=self.request.user)
        except Clinic.DoesNotExist:
            raise utils.get_api_exception("You are not associated with any clinic, Please request your admin",
                                          status.HTTP_406_NOT_ACCEPTABLE)
        serializer.save(clinic=clinic)


class SlotView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [cp.ManagerPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.SlotSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(Slot, pk=pk, clinic__manager=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ClinicAppointmentsView(generics.ListAPIView):
    permission_classes = [cp.ManagerPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        clinic = get_object_or_404(Clinic, manager=self.request.user)
        return Appointment.objects.filter(slot__clinic=clinic)


class UpdateAppointmentStatus(generics.RetrieveUpdateAPIView):
    permission_classes = [cp.ManagerPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.ManagerAppointmentSerializer
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs['pk']
        clinic = get_object_or_404(Clinic, manager=self.request.user)
        return get_object_or_404(Appointment, pk=pk, slot__clinic=clinic)


""" PATIENT APIS """


class CustomerAppointmentView(generics.ListAPIView):
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user)


class AppointmentHistory(generics.ListAPIView):
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(patient=self.request.user, status='Complete')


class CreateAppointmentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]

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
