from django.urls import path

from .views import CheckoutView, CancelSubscriptionView, DeleteAccountView


app_name = "billing"

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("cancel-subscription/", CancelSubscriptionView.as_view(), name="cancel_subscription"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]

