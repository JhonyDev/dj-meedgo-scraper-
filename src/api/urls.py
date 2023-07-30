from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('search-medicine/', views.ScrapeMedicineAPIView.as_view()),
    path('run-task/<int:object_id>/', views.custom_method_view, name='object-celery'),
    path('run-task/<int:object_id>/all/', views.custom_method_all_view, name='object-celery-all'),

]
