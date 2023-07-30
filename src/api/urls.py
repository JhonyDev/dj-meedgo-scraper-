from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('search-medicine/', views.ScrapeMedicineAPIView.as_view()),
    path('search-netmeds/', views.ScrapeNetmedsAPIView.as_view()),
    path('search-pharmeasy/', views.ScrapePharmeasyAPIView.as_view()),
    path('search-one-mg/', views.ScrapeOneMgAPIView.as_view()),
    path('search-flipkart/', views.ScrapeFlipkartAPIView.as_view()),
    path('run-task/<int:object_id>/', views.custom_method_view, name='object-celery'),
    path('run-task/<int:object_id>/all/', views.custom_method_all_view, name='object-celery-all'),

]
