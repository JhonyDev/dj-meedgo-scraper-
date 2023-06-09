from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomLoginView, CustomRegisterAccountView, UserUpdateView, LicensesListView, \
    LicenseEntryListCreateView, LicenseEntryRUDView, PhoneOTPLoginView, OTPVerificationView, UserTimeViewSet, \
    ChangePasswordView

app_name = 'accounts'
router = DefaultRouter()
router.register(r'user-time', UserTimeViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('login/', CustomLoginView.as_view(), name='login-user'),
    path('registration/', CustomRegisterAccountView.as_view(), name='account_create_new_user'),
    path('licenses/', LicensesListView.as_view(), name='licenses'),

    path('change-password/', ChangePasswordView.as_view()),

    path('otp-login/', PhoneOTPLoginView.as_view(), name='phone_otp_login'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp_verification'),

    path('my/profile/', UserUpdateView.as_view()),
    path('my/licenses/', LicenseEntryListCreateView.as_view(), name='license-entry'),
    path('my/licenses/<int:pk>/', LicenseEntryRUDView.as_view(), name='license-entry-RUD'),
]
