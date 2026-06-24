import stripe
from django.conf import settings
from urllib3 import request

stripe.api_key = settings.STRIPE_TOKEN


class StripeService:
    @staticmethod
    def create_checkout_session(request, plan):
        print(stripe.api_key)
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            success_url="https://seusite.com/sucesso",
            cancel_url="https://seusite.com/cancelado",
        )
        return checkout_session