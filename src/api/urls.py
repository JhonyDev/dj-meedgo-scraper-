from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name = 'api'

urlpatterns = [
    path('my/profile/', views.UserInformationGetView.as_view(), name='profile-info-get-update'),
    path('my/profile/image/', views.UserImageGetUpdateView.as_view(), name='user-image-update'),
    path('my/password/change/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
    path('my/news-feed/', views.UserNewsFeedView.as_view(), name='user-news-feed'),
    path('my/likes/', views.UserLikesGetView.as_view(), name='user-likes'),
    path('my/likers/', views.UserLikersGetView.as_view(), name='user-likers'),
]
