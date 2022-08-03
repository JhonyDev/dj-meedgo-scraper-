import datetime

from allauth.account.models import EmailAddress
from django.db.models import Q
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from . import permissions as cp
from . import serializers
from . import utils
from .models import Clinic, Slot, Appointment, UserDetail, RawImage, Images
from .serializers import UserChildSerializer, ImagesSimpleSerializer, AppointmentSerializer
from ..accounts.authentication import JWTAuthentication
from ..accounts.models import User
from ..accounts.serializers import CustomRegisterAccountSerializer


class PostRegistrationFormView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserDetail.objects.all()

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
        email = self.request.data.get('email')
        pk = self.kwargs["pk"]
        user = User.objects.get(pk=pk)
        if user.email != email:
            if EmailAddress.objects.filter(email=email):
                raise utils.get_api_exception('Email is already registered', status.HTTP_406_NOT_ACCEPTABLE)
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


class AvailableClinics(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    serializer_class = serializers.ClinicManagerSerializer

    def get_queryset(self):
        return Clinic.objects.all()


"""----------------------------VIEW SETS-----------------------------"""


class CustomAppointmentApi(APIView):
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        slot = request.data.get('slot')
        patient = request.data.get('patient')
        try:
            slot = Slot.objects.get(pk=slot)
        except Slot.DoesNotExist:
            raise utils.get_api_exception("Slot not found", status.HTTP_404_NOT_FOUND)

        try:
            patient = User.objects.get(pk=patient)
        except User.DoesNotExist:
            raise utils.get_api_exception("User not found", status.HTTP_404_NOT_FOUND)

        if Appointment.objects.filter(patient=patient, slot=slot).exists():
            raise utils.get_api_exception("Appointment already exists", status.HTTP_409_CONFLICT)

        appointment = Appointment.objects.create(patient=patient, slot=slot)
        id_keys = request.data.get('id_keys')
        insurance_keys = request.data.get('insurance_keys')
        if id_keys is None and insurance_keys is None:
            return Response(data={"message": "Appointment created successfully"},
                            status=status.HTTP_201_CREATED)

        if id_keys is not None:
            id_keys = id_keys.split(',')
        if insurance_keys is not None:
            insurance_keys = insurance_keys.split(',')
        for id in id_keys:
            Images.objects.create(appointment=appointment, image=request.data.get(id), image_type="ID")

        for id in insurance_keys:
            Images.objects.create(appointment=appointment, image=request.data.get(id), image_type="Insurance")

        return Response(data={"message": "Appointment created successfully"},
                        status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        relatives = list(User.objects.filter(related_to=self.request.user))
        appointments = Appointment.objects.filter(Q(patient=self.request.user) | Q(patient__in=relatives))
        return Response(data=AppointmentSerializer(appointments, many=True).data,
                        status=status.HTTP_200_OK)


class CustomerSlotsViewSets(generics.ListAPIView):
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]
    serializer_class = serializers.CustomerSlotSerializer

    def get_queryset(self):
        date = self.kwargs.get('date')
        try:
            target_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except:
            raise utils.get_api_exception("Date format incorrect", status.HTTP_400_BAD_REQUEST)
        clinic_pk = self.kwargs.get('clinic_pk')

        appointments = Appointment.objects.filter(patient=self.request.user).values("slot__pk")
        slots = []
        for appointment in appointments:
            slots.append(appointment["slot__pk"])

        slots = Slot.objects.filter(date=date, clinic__pk=clinic_pk, is_active=True).exclude(pk__in=slots)
        if target_date <= datetime.date.today():
            slots = Slot.objects.none()
        return slots


class CustomerAppointmentRUView(APIView):
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission]
    authentication_classes = [JWTAuthentication]

    def put(self, request, pk, format=None):
        slot = request.data.get('slot')
        patient = request.data.get('patient')
        print(request.data)
        slot = Slot.objects.get(pk=slot)
        patient = User.objects.get(pk=patient)
        appointment = Appointment.objects.get(pk=pk)
        if slot == appointment.slot and patient == appointment.patient:
            pass
        else:
            if Appointment.objects.filter(slot=slot, patient=patient).exists():
                raise utils.get_api_exception("Appointment already exists", status.HTTP_409_CONFLICT)
            appointment.slot = slot
            appointment.patient = patient
        id_keys = request.data.get('id_keys')
        insurance_keys = request.data.get('insurance_keys')
        if id_keys is None and insurance_keys is None:
            return Response(data={"message": "Appointment updated successfully"},
                            status=status.HTTP_201_CREATED)

        for id in id_keys:
            Images.objects.create(appointment=appointment, image=request.data.get(id), image_type="ID")

        for id in insurance_keys:
            Images.objects.create(appointment=appointment, image=request.data.get(id), image_type="Insurance")

        appointment.save()
        return Response(data={"message": "Appointment updated successfully"},
                        status=status.HTTP_201_CREATED)

    def get(self, request, pk, *args, **kwargs):
        appointments = Appointment.objects.get(pk=pk)
        return Response(data=AppointmentSerializer(appointments, many=False).data,
                        status=status.HTTP_200_OK)


class MyRelativesView(generics.ListCreateAPIView):
    serializer_class = UserChildSerializer
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission | cp.SubAdminPermission]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return User.objects.filter(related_to=self.request.user)

    def perform_create(self, serializer):
        user = serializer.save()
        EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
        user.related_to = self.request.user
        user.type = 'Patient'
        user.save()


class MyRelativesRUView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserChildSerializer
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission | cp.SubAdminPermission]
    authentication_classes = [JWTAuthentication]
    lookup_field = 'pk'

    def get_object(self):
        pk = self.kwargs["pk"]
        return get_object_or_404(User, pk=pk, related_to=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ImagePostTest(generics.ListCreateAPIView):
    serializer_class = ImagesSimpleSerializer
    permission_classes = [cp.PatientPermission | cp.SuperAdminPermission | cp.SubAdminPermission]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return RawImage.objects.all()

    def perform_create(self, serializer):
        serializer.save()
