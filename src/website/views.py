from django.views.generic import TemplateView


class ReturnsRefundsView(TemplateView):
    template_name = "website/refunds_returns.html"


class AboutUsView(TemplateView):
    template_name = "website/about_us.html"


class PrivacyPolicyView(TemplateView):
    template_name = "website/privacy_policy.html"


class TermsConditionsView(TemplateView):
    template_name = "website/terms_conditions.html"
