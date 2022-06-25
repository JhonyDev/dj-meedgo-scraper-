from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

    path('', views.APIHomeView.as_view(), name='user-view'),

]
