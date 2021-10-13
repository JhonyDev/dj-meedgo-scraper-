from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from src.api.models import Like, FriendList
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from src.accounts.models import User, UserImage
from src.api.bll import create_like_logic, subscription_logic

from .serializers import (
    UserImageSerializer,
    UserNewsFeedSerializer,
    UserPasswordChangeSerializer, UserSerializer, UserFriendListSerializer, LikeSerializer
)


class UserProfileDetailedView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = User.objects.get(pk=self.request.user.pk)
        return user


class UserNewsFeedListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserNewsFeedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        users = User.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        liked_users = Like.objects.filter(liked_by=self.request.user)
        users = users.exclude(pk__in=liked_users)
        return users


class UserLikersListView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['like_type']

    def get_queryset(self):
        return Like.objects.filter(liked_to=self.request.user)


class UserLikesListView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['like_type']

    def get_queryset(self):
        return Like.objects.filter(liked_by=self.request.user)


""" AUTH --- """


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


""" LIKES AND FRIENDS """


class UserLikeCreateView(APIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response_message, response_code = create_like_logic(request)
        return Response(data=response_message, status=response_code)


class UserSubscribe(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        response_message, response_code = subscription_logic(request)
        return Response(data=response_message, status=response_code)


class UserFriendsListView(generics.ListAPIView):
    queryset = FriendList.objects.all()
    serializer_class = UserFriendListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FriendList.objects.filter(user=self.request.user)


class UserLikeDeleteView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        like_id = self.kwargs['pk']
        return get_object_or_404(Like.objects.filter(liked_by=self.request.user), pk=like_id)


""" IMAGES VIEWS --- """


class UserImagesListCreateView(generics.ListCreateAPIView):
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserImageDeleteView(generics.RetrieveDestroyAPIView):
    queryset = FriendList.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        image_id = self.kwargs['pk']
        return get_object_or_404(UserImage.objects.filter(user=self.request.user), pk=image_id)
