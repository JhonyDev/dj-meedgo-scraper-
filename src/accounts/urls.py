from django.urls import path

from .views import CustomLoginView, CustomRegisterAccountView

app_name = 'accounts'
urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login-user'),
    path('registration/', CustomRegisterAccountView.as_view(), name='account_create_new_user'), ]
