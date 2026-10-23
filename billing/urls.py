from django.urls import path

from .views import CheckoutView, CancelSubscriptionView, DeleteAccountView, StripePortalView
from .webhooks_views import stripe_webhook


app_name = "billing"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("portal/", StripePortalView.as_view(), name="portal"),
    path("cancel-subscription/", CancelSubscriptionView.as_view(), name="cancel_subscription"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
]


