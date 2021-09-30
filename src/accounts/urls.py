from django.urls import path

from .views import view_activate  # LoginView, LogoutView

app_name = 'accounts'
urlpatterns = [
    # path('login/', LoginView.as_view(), name='administration-login'),
    # path('logout/', LogoutView.as_view(), name='administration-logout'),

    path('activate/<uidb64>/<token>/', view_activate, name='activate'),
]
