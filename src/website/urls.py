from django.urls import path

from .views import PrivacyPolicyView, TermsConditionsView

app_name = 'website'
urlpatterns = [
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-conditions/', TermsConditionsView.as_view(), name='terms-conditions'),
]
