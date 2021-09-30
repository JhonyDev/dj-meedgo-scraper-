from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers

from . import views

app_name = 'api'

urlpatterns = [
    path('my/profile/', views.GetUserViewSet.as_view(), name='profile-info-retrieve'),
    path('my/profile/image/', views.UserImageUpdateView.as_view(), name='user-image-update'),
    path('my/password/change/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
]
