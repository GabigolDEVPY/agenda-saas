import stripe
from django.conf import settings
from django.urls import reverse

# Configure Stripe API key
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)


class StripeService:
    @staticmethod
    def create_checkout_session(request, plan):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)
        
        # Check if the user already has a Stripe customer ID
        subscription = getattr(request.user, 'subscription', None)
        customer_id = subscription.stripe_customer_id if subscription else None
        
        # Build dynamic return URLs
        success_url = request.build_absolute_uri(
            reverse('admin_portal:home') + '?tab=conta&payment=success'
        )
        cancel_url = request.build_absolute_uri(
            reverse('admin_portal:home') + '?tab=conta&payment=cancelled'
        )
        
        checkout_kwargs = {
            "payment_method_types": ["card"],
            "mode": "subscription",
            "line_items": [
                {
                    "price": plan.stripe_price_id,
                    "quantity": 1,
                }
            ],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(request.user.id),
            "subscription_data": {
                "metadata": {
                    "user_id": str(request.user.id),
                    "plan_id": str(plan.id),
                }
            },
            "metadata": {
                "user_id": str(request.user.id),
                "plan_id": str(plan.id),
            }
        }
        
        # If customer already exists, associate checkout session with them
        if customer_id:
            checkout_kwargs["customer"] = customer_id
        else:
            checkout_kwargs["customer_email"] = request.user.email
            
        checkout_session = stripe.checkout.Session.create(**checkout_kwargs)
        return checkout_session

    @staticmethod
    def create_portal_session(request, customer_id):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)
        
        return_url = request.build_absolute_uri(
            reverse('admin_portal:home') + '?tab=conta'
        )
        
        portal_session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return portal_session

    @staticmethod
    def get_payment_method_details(customer_id):
        if not customer_id:
            return None
            
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)
        
        try:
            # List the customer's active cards
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            if payment_methods.data:
                card = payment_methods.data[0].card
                return {
                    "brand": card.brand,
                    "last4": card.last4,
                    "exp_month": card.exp_month,
                    "exp_year": card.exp_year,
                }
        except Exception as e:
            # Fail silently on network/Stripe API errors to avoid breaking the dashboard
            print(f"Error fetching card details from Stripe: {e}")
            
        return None