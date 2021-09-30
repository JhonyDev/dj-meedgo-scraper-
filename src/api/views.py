from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from src.accounts.models import User


from .serializers import (
    UserImageSerializer,
    UserPasswordChangeSerializer, UserSerializer
)


class UserInformationGetView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.get(pk=self.request.user.pk)
        return user


class UserImageGetUpdateView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.get(pk=self.request.user.pk)
        return user


class UserPasswordChangeView(generics.UpdateAPIView):
    model = User
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)