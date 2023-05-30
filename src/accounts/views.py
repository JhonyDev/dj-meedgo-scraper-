from allauth.account.models import EmailAddress
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts import authentication
from src.accounts.serializers import CustomRegisterAccountSerializer, CustomLoginSerializer
from src.api.serializers import UserSerializer


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
