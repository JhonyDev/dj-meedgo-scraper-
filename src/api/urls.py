from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('my/profile/', views.UserDetailsView.as_view()),
    path('users/', views.UsersListView.as_view()),
    path('user/<int:pk>/', views.UserDetailsView.as_view()),

    path('rooms/', views.RoomsListView.as_view()),
    path('room/<int:pk>/', views.RoomRUV.as_view()),

    path('categories/', views.CategoryListView.as_view()),
    path('num/categories/', views.CategoryCreateView.as_view()),
    path('num/categories/<int:pk>/', views.CategoryNumRUV.as_view()),
    path('category/<int:pk>/', views.CategoryRUV.as_view()),

    path('admin/bookings/', views.BookingListViewGeneral.as_view()),
    path('admin/booking/<int:pk>/', views.BookingListViewGeneral.as_view()),
    path('create/booking/', views.BookingAPIView.as_view()),
    path('bookings/', views.BookingListView.as_view()),
    path('booking/<int:pk>/', views.BookingListView.as_view()),

    path('today/availability/', views.AvailabilityToday.as_view()),
    path('date/availability/<str:date_>/', views.AvailabilityTargetDate.as_view()),

    path('admin/bookings/month/<str:month>/year/<str:year>/', views.BookingsMonthGeneral.as_view()),
    path('bookings/month/<str:month>/year/<str:year>/', views.BookingsMonth.as_view()),

]
