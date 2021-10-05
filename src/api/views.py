from django.http import Http404

from src.api.models import Like, FriendList
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from src.accounts.models import User, UserImage

from .serializers import (
    UserImageSerializer, UserLikersSerializer, UserLikesSerializer,
    UserNewsFeedSerializer,
    UserPasswordChangeSerializer, UserSerializer, UserFriendListSerializer
)


class UserInformationGetView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.get(pk=self.request.user.pk)
        return user


class UserNewsFeedView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserNewsFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()


class UserLikersGetView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserLikersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(liked_to=self.request.user)


class UserLikesGetView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserLikesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Like.objects.filter(liked_by=self.request.user)


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


" LIKES LOGICS "


class UserLikeDeleteView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        like_id = self.kwargs['id']
        objects = Like.objects.filter(pk=like_id, liked_by=self.request.user)
        if objects:
            return objects.first()
        else:
            return Http404


class UserFriendsListView(generics.ListAPIView):
    queryset = FriendList.objects.all()
    serializer_class = UserFriendListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendList.objects.filter(user=self.request.user)


class UserImageDeleteView(generics.RetrieveDestroyAPIView):
    queryset = FriendList.objects.all()
    serializer_class = UserFriendListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        image_id = self.kwargs['id']
        user_images = UserImage.objects.filter(pk=image_id, user=self.request.user)

        if user_images:
            return user_images.first()
        else:
            return Http404
