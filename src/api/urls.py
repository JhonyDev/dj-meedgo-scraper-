from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import UserRatingViewSet

app_name = 'api'
router = DefaultRouter()
router.register(r'rating', UserRatingViewSet)

urlpatterns = [

    path('', include(router.urls)),
    path('my/ratings/', views.UserRatingListView.as_view()),

    path('search-medicine/', views.MedicineSearchView.as_view()),
    path('cart/', views.MedicineToCartView.as_view()),
    path('alternate-medicine/<int:medicine_pk>/', views.AlternateMedicineView.as_view()),

    path('order-requests/', views.OrderRequestsView.as_view()),
    path('order-requests/<int:pk>/update/', views.OrderRequestUpdateView.as_view()),

    path('locality/order-requests/', views.OrderRequestsLocalityView.as_view()),
    path('grab-orders/', views.GrabOrdersView.as_view()),
    path('grab-orders/<int:pk>/', views.GrabOrderDetailView.as_view()),
    path('medicine-offer/<int:pk>/', views.MedicineOfferUpdateView.as_view()),
    path('my/conversations/', views.ConversationHistoryListView.as_view()),
    path('my/conversations/<int:pk>/', views.MessageListView.as_view()),

    path('initiate-payment/', views.InitiatePaymentView.as_view(), name='initiate-payment'),
    path('callback/', views.CallbackView.as_view(), name='callback'),

    # ADMIN PANEL SCRAPE TASK
    path('run-task/<int:object_id>/', views.custom_method_view, name='object-celery'),
    path('run-task/<int:object_id>/all/', views.custom_method_all_view, name='object-celery-all'),

    # Test API VIEW
    path('', views.lobby),
    path('payment-test/', views.test),

]
