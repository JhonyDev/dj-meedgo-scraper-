from django.urls import path

from .views import PrivacyPolicyView, TermsConditionsView, AboutUsView, ReturnsRefundsView

app_name = 'website'
urlpatterns = [
    path('returns-refunds/', ReturnsRefundsView.as_view(), name='returns-refunds'),
    path('about-us/', AboutUsView.as_view(), name='about-us'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('terms-conditions/', TermsConditionsView.as_view(), name='terms-conditions'),
]
