from allauth.account.models import EmailAddress
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts import authentication
from src.accounts.authentication import JWTAuthentication
from src.accounts.models import License, LicenseEntry
from src.accounts.serializers import CustomRegisterAccountSerializer, CustomLoginSerializer, LicenseSerializer, \
    LicenseEntrySerializer
from src.api.serializers import UserSerializer, UserProfileSerializer


class UserUpdateView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class CustomRegisterAccountView(APIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        status_code = status.HTTP_400_BAD_REQUEST
        serializer = CustomRegisterAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if user.email:
                EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            access_token = authentication.create_access_token(UserSerializer(user).data)
            refresh_token = authentication.create_refresh_token(user.pk)
            data = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            status_code = status.HTTP_201_CREATED
        else:
            data = serializer.errors
        return Response(data=data, status=status_code)


class CustomLoginView(APIView):
    serializer_class = CustomLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        response = Response()
        user_serializer = UserSerializer(user)
        access_token = authentication.create_access_token(user_serializer.data)
        refresh_token = authentication.create_refresh_token(user.pk)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response


class LicensesListView(generics.ListAPIView):
    serializer_class = LicenseSerializer
    queryset = License.objects.all()
    permission_classes = [permissions.AllowAny]


class LicenseEntryListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = LicenseEntrySerializer
    queryset = LicenseEntry.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()


class LicenseEntryRUDView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = LicenseEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LicenseEntry.objects.all()
