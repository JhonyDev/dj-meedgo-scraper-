from django.urls import path

from .views import CustomLoginView, CustomRegisterAccountView, UserUpdateView, LicensesListView, \
    LicenseEntryListCreateView, LicenseEntryRUDView

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login-user'),
    path('registration/', CustomRegisterAccountView.as_view(), name='account_create_new_user'),
    path('licenses/', LicensesListView.as_view(), name='licenses'),

    path('my/profile/', UserUpdateView.as_view()),
    path('my/licenses/', LicenseEntryListCreateView.as_view(), name='license-entry'),
    path('my/licenses/<int:pk>/', LicenseEntryRUDView.as_view(), name='license-entry-RUD'),

]
