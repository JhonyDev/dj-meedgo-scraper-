# Create your views here.
from rest_framework import generics, permissions

from src.accounts.authentication import JWTAuthentication
from src.notification.models import Notification
from src.notification.serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)[:10]
