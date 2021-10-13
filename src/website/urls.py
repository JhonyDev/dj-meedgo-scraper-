from django.urls import path
from django.views.generic import TemplateView


app_name = 'website'

urlpatterns = [
    path('', TemplateView.as_view(template_name='website/home.html'), name='home'),
    path('privacy-policy/', TemplateView.as_view(template_name='website/privacy_policy.html'), name='privacy-policy'),
    path('terms/', TemplateView.as_view(template_name='website/terms.html'), name='terms'),
]
