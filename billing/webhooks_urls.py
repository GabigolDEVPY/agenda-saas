# urls.py
from django.urls import path
from .webhooks_views import stripe_webhook

urlpatterns = [
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
]