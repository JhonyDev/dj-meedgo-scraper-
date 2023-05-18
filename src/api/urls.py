from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('search-medicine/', views.MedicineSearchView.as_view()),
    path('cart/', views.MedicineToCartView.as_view()),
    path('alternate-medicine/<int:medicine_pk>/', views.AlternateMedicineView.as_view()),
    path('order-requests/', views.OrderRequestsView.as_view()),
]
