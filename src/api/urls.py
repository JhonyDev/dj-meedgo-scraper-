from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('search-medicine/', views.MedicineSearchView.as_view()),
    path('cart/', views.MedicineToCartView.as_view()),
]
