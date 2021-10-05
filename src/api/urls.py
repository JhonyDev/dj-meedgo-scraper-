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

    path('like/<int:pk>/delete/', views.UserLikeDeleteView.as_view(), name='like-delete'),
    path('image/<int:pk>/delete/', views.UserImageDeleteView.as_view(), name='image-get-delete'),
    path('my/images/', views.UserImagesListView.as_view(), name='user-images-get'),
    path('like/user/<int:pk>/', views.LikeUserView.as_view(), name='like-user-post')

]
