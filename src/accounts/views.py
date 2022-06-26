from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import permissions, status
from rest_framework.authtoken.models import TokenProxy
from rest_framework.response import Response
from rest_framework.views import APIView

from core.settings import GOOGLE_CALLBACK_ADDRESS
from src.accounts.serializers import CustomRegisterAccountSerializer


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = GOOGLE_CALLBACK_ADDRESS


class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class CustomRegisterAccountView(APIView):
    serializer_class = CustomRegisterAccountSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        status_code = status.HTTP_400_BAD_REQUEST
        serializer = CustomRegisterAccountSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            token = TokenProxy.objects.create(user=user)
            data = {'key': f'{token}'}
            status_code = status.HTTP_201_CREATED
        else:
            data = serializer.errors
        return Response(data=data, status=status_code)
