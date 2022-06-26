from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('registration/details/', views.PostRegistrationFormView.as_view(), name='user-view'),

]
