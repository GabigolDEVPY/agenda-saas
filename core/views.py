from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = "core/landing.html"


class PrivacyView(TemplateView):
    template_name = "core/privacy.html"
