from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from src.api.models import Like, FriendList, Report
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from src.accounts.models import User, UserImage
from src.api.bll import create_like_logic, subscription_logic

from .serializers import (
    UserImageSerializer,
    UserPasswordChangeSerializer, UserSerializer, FriendSerializer, LikeSerializer, ReportSerializer,
    LikeAddSerializer, UserPublicSerializer
)


class UserProfileDetailedView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserNewsFeedListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):


        users = User.objects.filter(is_active=True, is_superuser=False, is_staff=False)
        # liked_users = Like.objects.filter(liked_by=self.request.user)
        users = User.objects.filter(
            is_active=True, is_superuser=False, is_staff=False,
            interested_in_gender=self.request.user.interested_in_gender,
            interested_lower_age__gte=self.request.user.interested_lower_age,
            interested_upper_age__lte=self.request.user.interested_upper_age
        )
        liked_users = Like.objects.filter(liked_by=self.request.user)
        reported_users = Report.objects.filter(user=self.request.user)

        r_u = []
        # [l_u.append(x.liked_to.pk) for x in liked_users]
        [r_u.append(x.target.pk) for x in reported_users]

        users = users.exclude(pk__in=r_u)
        # users = users.exclude(pk__in=l_u)

        return users.exclude(pk__in=r_u)


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
    serializer_class = LikeAddSerializer
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
    serializer_class = FriendSerializer
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


class UserReportsListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)


class ReportUserCreateView(APIView):
    queryset = Report.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        user = get_object_or_404(User.objects.all(), pk=pk)

        if request.user == user:
            return Response(
                data={"message": "you can't report yourself"}, status=status.HTTP_400_BAD_REQUEST
            )

        if Report.objects.filter(user=request.user, target=user):
            return Response(
                data={'message': 'Requested user already reported'}, status=status.HTTP_208_ALREADY_REPORTED
            )

        report = Report(user=request.user, target=user)
        report.save()
        return Response(
            data={
                'message': f'You have successfully reported {user.username} - '
                           f'our team will investigate the issue.'
                  },
            status=status.HTTP_201_CREATED
        )
