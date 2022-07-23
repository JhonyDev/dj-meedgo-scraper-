from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'', views.CustomerAppointmentView, basename='customer-appointment')
app_name = 'api'

urlpatterns = [
    path('registration/details/', views.PostRegistrationFormView.as_view(), name='reg-details'),
    path('my/profile/', views.UserDetailsView.as_view(), name='my-profile'),

    path('admin/managers/', views.MyManagersView.as_view(), name='admin-mangers'),
    path('admin/managers/<int:pk>/', views.ManagerView.as_view(), name='admin-manager-view'),
    path('admin/clinics/', views.MyClinicsView.as_view(), name='admin-clinics'),
    path('admin/clinics/<int:pk>/', views.MyClinicRUView.as_view(), name='admin-clinic-view'),

    path('manager/clinic/', views.ClinicView.as_view(), name='manager-clinic-view'),
    path('manager/slots/', views.SlotsView.as_view(), name='manager-slots'),
    path('manager/slots/<int:pk>/', views.SlotView.as_view(), name='manager-slot-view'),
    path('manager/clinic/appointments/', views.ClinicAppointmentsView.as_view(), name='clinic-appointments'),
    path('manager/clinic/appointments/<int:pk>/', views.UpdateAppointmentStatus.as_view(),
         name='update-status-appointment'),

    path('available/clinics/', views.AvailableClinics.as_view(), name='available-appointment'),
    # path('customer/clinic/slots/<int:pk>/', views.CustomerClinicSlots.as_view(),
    #      name='available-appointment'),
    path('customer/appointments/', include(router.urls)),
    path('customer/slots/date/<str:date>/clinic/<int:clinic_pk>/', views.CustomerSlotsViewSets.as_view(),
         name='customer-slots'),
    path('create/appointment/slot/<int:pk>/', views.CreateAppointmentView.as_view(), name='create-appointment'),
    path('customer/history/appointments/', views.AppointmentHistory.as_view(),
         name='customer-history-appointment'),

]
