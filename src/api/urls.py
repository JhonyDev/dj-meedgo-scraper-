from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

    path('my/profile/', views.UserInformationGetView.as_view(), name='profile-info-get-put'),
    path('my/profile/details/', views.UserInformationGetView.as_view(), name='profile-info-details-get'),

    path('my/password/change/', views.UserPasswordChangeView.as_view(), name='user-password-chang-put'),
    path('my/news-feed/', views.UserNewsFeedView.as_view(), name='user-news-feed-get'),
    path('my/likes/', views.UserLikesGetView.as_view(), name='user-likes-get'),
    path('my/likers/', views.UserLikersGetView.as_view(), name='user-likers-get'),

]
