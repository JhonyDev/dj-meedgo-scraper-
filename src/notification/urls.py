from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('my/notifications/', views.NotificationListView.as_view()),
]
