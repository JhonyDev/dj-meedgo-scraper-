from django.views.generic import TemplateView


class PrivacyPolicyView(TemplateView):
    template_name = "website/privacy_policy.html"


class TermsConditionsView(TemplateView):
    template_name = "website/terms_conditions.html"
