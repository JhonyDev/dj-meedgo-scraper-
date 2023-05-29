from django.urls import re_path

from core import consumers

websocket_urlpatterns = [
    re_path(r'wss/socket-server/', consumers.NotificationConsumer.as_asgi())
]
