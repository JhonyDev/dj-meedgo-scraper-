from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('', views.lobby),
    path('search-medicine/', views.MedicineSearchView.as_view()),
    path('cart/', views.MedicineToCartView.as_view()),
    path('alternate-medicine/<int:medicine_pk>/', views.AlternateMedicineView.as_view()),
    path('order-requests/', views.OrderRequestsView.as_view()),
    path('locality/order-requests/', views.OrderRequestsLocalityView.as_view()),
    path('grab-orders/', views.GrabOrdersView.as_view()),
    path('grab-orders/<int:pk>/', views.GrabOrderDetailView.as_view()),
    path('medicine-offer/<int:pk>/', views.MedicineOfferUpdateView.as_view()),

    # ADMIN PANEL SCRAPE TASK
    path('run-task/<int:object_id>/', views.custom_method_view, name='object-celery'),
]
