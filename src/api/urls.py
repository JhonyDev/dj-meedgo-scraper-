from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

    path('my/profile/', views.UserProfileDetailedView.as_view(), name='profile-info-view-update'),
    path('my/profile/details/', views.UserProfileDetailedView.as_view(), name='profile-info-details-get'),
    path('my/images/', views.UserImagesListCreateView.as_view(), name='user-images-view-create-image'),
    path('image/<int:pk>/', views.UserImageDeleteView.as_view(), name='image-view-delete'),
    path('my/password/change/', views.UserPasswordChangeView.as_view(), name='user-password-chang-put'),
    path('my/likes/', views.UserLikesListView.as_view(), name='user-likes-get'),
    path('my/likers/', views.UserLikersListView.as_view(), name='user-likers-get'),
    path('like/<int:pk>/delete/', views.UserLikeDeleteView.as_view(), name='like-delete'),

    path('like/user/', views.UserLikeCreateView.as_view(), name='like-user-post'),
    path('subscribe/', views.UserSubscribe.as_view(), name='subscribe-user'),

    path('my/news-feed/', views.UserNewsFeedListView.as_view(), name='user-news-feed-get'),

]
