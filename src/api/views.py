from base64 import b64encode
from datetime import datetime, date

import requests
from dateutil.relativedelta import relativedelta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth

from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view

from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import filters as filterz
from rest_framework import generics, viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from core import settings

from src.api.models import Like, FriendList, Report, MpesaTransaction
from src.accounts.models import User, UserImage
from src.api.bll import create_like_logic, subscription_logic

from .serializers import (
    UserImageSerializer,
    UserPasswordChangeSerializer, UserSerializer, FriendSerializer, LikeSerializer, ReportSerializer,
    LikeAddSerializer, UserPublicSerializer, MpesaTransactionSerializer
)

consumer_k = settings.CONSUMER_KEY
consumer_s = settings.CONSUMER_SECRET
pass_key = settings.PASSKEY
s_code = settings.SHORT_CODE
c_url = settings.CALLBACK_URL


class UserPublicDetailedView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileDetailedView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserNewsFeedListView(generics.ListAPIView):
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        if self.request.user.interested_in_gender != 'o':
            users = User.objects.filter(
                is_active=True, is_superuser=False, is_staff=False,
                gender=self.request.user.interested_in_gender,
                interested_lower_age__gte=self.request.user.interested_lower_age,
                interested_upper_age__lte=self.request.user.interested_upper_age
            )
        else:
            users = User.objects.filter(
                is_active=True, is_superuser=False, is_staff=False,
                interested_lower_age__gte=self.request.user.interested_lower_age,
                interested_upper_age__lte=self.request.user.interested_upper_age
            )

        reported_users = Report.objects.filter(user=self.request.user)

        r_u = []
        [r_u.append(x.target.pk) for x in reported_users]

        users = users.exclude(pk__in=r_u).exclude(profile_image=None)
        users = users.exclude(pk=self.request.user.pk)

        return users.exclude(pk__in=r_u).order_by('?')[:50]


class UserLikersListView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['like_type']

    def get_queryset(self):
        return Like.objects.filter(liked_to=self.request.user).exclude(liked_by=self.request.user.pk)


class UserLikesListView(generics.ListAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['like_type']

    def get_queryset(self):
        return Like.objects.filter(liked_by=self.request.user).exclude(liked_to=self.request.user)


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
        return FriendList.objects.filter(user=self.request.user).exclude(friend=self.request.user)


class UserLikeDeleteView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        like_id = self.kwargs['pk']
        return get_object_or_404(Like.objects.filter(liked_by=self.request.user), pk=like11111_id)


""" IMAGES VIEWS --- """


class UserImagesListCreateView(generics.ListCreateAPIView):
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicUserImage(generics.ListCreateAPIView):
    queryset = UserImage.objects.all()
    serializer_class = UserImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return UserImage.objects.filter(image=None)

    def perform_create(self, serializer):
        serializer.save(user=User.objects.get(pk=1))


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


""" MPAISA END-POINTS """


@method_decorator(csrf_exempt, name='dispatch')
class MpesaSTKApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, **kwargs):
        data = request.data

        if "user_id" and "user_phone" in data.keys():
            try:
                user = User.objects.get(
                    pk=data["user_id"])
            except User.DoesNotExist:
                user = None

            if not user:
                return Response({'detail': 'Customer with that id does not exist, please confirm.'},
                                status=status.HTTP_404_NOT_FOUND)

            if "purpose" in data.keys():
                stk_purpose = data["purpose"]
            else:
                stk_purpose = "Subscription"

            if "amount" in data.keys():
                amount = data["amount"]
            else:
                amount = 2000
            Passkey = pass_key

            Shortcode = s_code
            callback_url = c_url

            def get_stk_token():
                consumer_key = consumer_k
                consumer_secret = consumer_s
                auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
                r = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
                access_token = r.json()['access_token']
                return access_token

            access_token = get_stk_token()

            def get_time():
                now = str(datetime.now().strftime("%Y%m%d"))
                time = str(datetime.now().strftime("%H%M%S"))
                real = str(now + time)
                return real

            time_now = get_time()

            def encoded_pass():
                pwd = (str(Shortcode) + Passkey + time_now).encode('utf-8')
                pwd_enc = b64encode(pwd).decode('ascii')
                return pwd_enc

            pass_enc = encoded_pass()

            api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": "Bearer %s" % access_token}

            request = {
                "BusinessShortCode": Shortcode,
                "Password": pass_enc,
                "Timestamp": time_now,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": data["user_phone"],
                "PartyB": Shortcode,
                "PhoneNumber": data["user_phone"],
                "CallBackURL": callback_url,
                "AccountReference": "4075259",
                "TransactionDesc": stk_purpose
            }

            activate_subscription = False

            """ IF USER DOESN't ACTIVATED PREVIOUSLY """
            if not user.is_paid:
                activate_subscription = True
            else:
                """ IF USER ACTIVATED PREVIOUSLY BUT EXPIRED"""
                if user.expiry_date < date.today():
                    activate_subscription = True
                else:
                    return Response({"detail": "Already subscribed"}, status=status.HTTP_200_OK)

            """ IF ALLOWED TO SUBSCRIBE """
            if activate_subscription:
                response = requests.post(api_url, json=request, headers=headers)
                # print(response.json())

                if response.status_code == 200:
                    MpesaTransaction.objects.create(
                        user_id=User.objects.get(pk=data["user_id"]),
                        user_phone=data["user_phone"],
                        purpose=stk_purpose,
                        amount=amount,
                        timestamp=time_now,
                        expires_on=date.today() + relativedelta(months=6),
                        request_id=response.json()["MerchantRequestID"],

                    )

            return Response({"detail": "Stk push Succesfull"}, status=status.HTTP_200_OK)

        else:
            return Response({"detail": "You need to pass the user phone number to make the stk push."},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


class MpesaSTKConfirmationApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, **kwargs):
        data = request.data
        if data["Body"]["stkCallback"]["ResultCode"] == 0:
            try:
                transaction = MpesaTransaction.objects.get(
                    request_id=data["Body"]["stkCallback"]["MerchantRequestID"])
            except MpesaTransaction.DoesNotExist:
                transaction = None

            if transaction:
                transaction.completed = True
                transaction.save()
            user_id = transaction.user_id
            # user = User.objects.get(user_id=user_id)
            user = user_id
            user.is_paid = True
            user.expiry_date = date.today() + relativedelta(months=6)
            user.save()
        return Response({"detail": "Done"}, status=status.HTTP_200_OK)


class MpesaTransactionsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MpesaTransactionSerializer
    queryset = MpesaTransaction.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filterz.SearchFilter)
    filterset_fields = ('user_id', 'user_phone', 'completed', 'purpose')
    search_fields = ['user_id', 'user_phone', 'purpose']
