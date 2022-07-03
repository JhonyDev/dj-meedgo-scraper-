from allauth.account.models import EmailAddress
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts import authentication
from src.accounts.models import User
from src.accounts.serializers import CustomRegisterAccountSerializer, CustomLoginSerializer
from src.api import utils
from src.api.models import UserDetail
from src.api.serializers import UserSerializer


class CustomRegisterAccountView(APIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        status_code = status.HTTP_400_BAD_REQUEST
        serializer = CustomRegisterAccountSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            access_token = authentication.create_access_token(UserSerializer(user).data,
                                                              not UserDetail.objects.filter(user=user).exists())
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
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise utils.get_api_exception('Invalid credential User invalid', status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            raise utils.get_api_exception('Invalid credential', status.HTTP_400_BAD_REQUEST)

        if user.type == "Manager":
            from src.api.models import Clinic
            try:
                Clinic.objects.get(manager=user)
            except Clinic.DoesNotExist:
                msg = 'Login forbidden! You are not associated with any clinic.'
                raise utils.get_api_exception(msg, status.HTTP_403_FORBIDDEN)

        response = Response()
        serializer = UserSerializer(user)
        access_token = authentication.create_access_token(serializer.data,
                                                          not UserDetail.objects.filter(user=user).exists())
        refresh_token = authentication.create_refresh_token(user.pk)
        response.data = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return response
