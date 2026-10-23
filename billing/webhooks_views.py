import stripe
import json
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import get_user_model

from billing.models import Subscription
from billing.services import LimitsService

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    event = None
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)

    # Developer Experience helper for local development
    if not getattr(settings, 'STRIPE_WEBHOOK_SECRET', None) and settings.DEBUG:
        try:
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except Exception as e:
            return HttpResponse(f"Invalid local payload: {str(e)}", status=400)
    else:
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            return HttpResponse("Signature verification failed", status=400)
        except Exception as e:
            return HttpResponse(f"Webhook error: {str(e)}", status=400)

    event_type = event["type"]
    data = event["data"]["object"]
    
    print(f"Stripe Webhook Event Received: {event_type}")

    # 1. CHECKOUT COMPLETED (First subscription purchase)
    if event_type == "checkout.session.completed":
        user_id = data.get("client_reference_id") or data.get("metadata", {}).get("user_id")
        customer_id = data.get("customer")
        stripe_sub_id = data.get("subscription")
        
        if user_id:
            User = get_user_model()
            user = User.objects.filter(id=user_id).first()
            if user:
                sub, created = Subscription.objects.get_or_create(
                    user=user,
                    defaults={"plan": LimitsService.get_default_plan()}
                )
                sub.stripe_customer_id = customer_id or ""
                sub.stripe_subscription_id = stripe_sub_id or ""
                
                # Fetch cycle information from Stripe
                if stripe_sub_id:
                    try:
                        stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
                        sub.expires_at = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.get_current_timezone())
                    except Exception as e:
                        print(f"Error retrieving subscription details on checkout: {e}")
                
                sub.status = Subscription.Status.ACTIVE
                sub.is_active = True
                sub.save()
                print(f"Subscription activated via checkout for user: {user.email}")

    # 2. INVOICE PAID (Subscription renewals and initial payment success)
    elif event_type == "invoice.paid":
        stripe_sub_id = data.get("subscription")
        customer_id = data.get("customer")
        
        sub = None
        if stripe_sub_id:
            sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub and customer_id:
            sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
            
        if sub and stripe_sub_id:
            try:
                stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
                sub.expires_at = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.get_current_timezone())
                sub.status = Subscription.Status.ACTIVE
                sub.is_active = True
                if not sub.stripe_subscription_id:
                    sub.stripe_subscription_id = stripe_sub_id
                if customer_id and not sub.stripe_customer_id:
                    sub.stripe_customer_id = customer_id
                sub.save()
                print(f"Subscription renewed/paid via invoice for user: {sub.user.email}")
            except Exception as e:
                print(f"Error updating subscription on invoice.paid: {e}")

    # 3. INVOICE PAYMENT FAILED (Recurring charge declined)
    elif event_type == "invoice.payment_failed":
        stripe_sub_id = data.get("subscription")
        customer_id = data.get("customer")
        
        sub = None
        if stripe_sub_id:
            sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub and customer_id:
            sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
            
        if sub:
            sub.status = Subscription.Status.PAST_DUE
            sub.is_active = False  # Block access immediately when payment fails
            sub.save()
            print(f"Subscription payment failed (past_due) for user: {sub.user.email}")

    # 4. SUBSCRIPTION DELETED (Cancelled or fully unpaid/expired in Stripe)
    elif event_type == "customer.subscription.deleted":
        stripe_sub_id = data.get("id")  # ID of the subscription itself
        customer_id = data.get("customer")
        
        sub = None
        if stripe_sub_id:
            sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub and customer_id:
            sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
            
        if sub:
            sub.status = Subscription.Status.CANCELED
            sub.is_active = False
            sub.stripe_subscription_id = ""  # Clear the subscription ID so they can subscribe again
            sub.save()
            print(f"Subscription deleted/canceled for user: {sub.user.email}")

    # 5. SUBSCRIPTION UPDATED (Plan change, cancellation toggled, etc.)
    elif event_type == "customer.subscription.updated":
        stripe_sub_id = data.get("id")
        customer_id = data.get("customer")
        stripe_status = data.get("status")
        cancel_at_period_end = data.get("cancel_at_period_end", False)
        current_period_end = data.get("current_period_end")
        
        sub = None
        if stripe_sub_id:
            sub = Subscription.objects.filter(stripe_subscription_id=stripe_sub_id).first()
        if not sub and customer_id:
            sub = Subscription.objects.filter(stripe_customer_id=customer_id).first()
            
        if sub:
            if current_period_end:
                sub.expires_at = datetime.fromtimestamp(current_period_end, tz=timezone.get_current_timezone())
            
            # Sync subscription status
            if stripe_status == "active":
                if cancel_at_period_end:
                    sub.status = Subscription.Status.CANCELED  # Cancelled recurring billing, but active until expires_at
                    sub.is_active = True
                else:
                    sub.status = Subscription.Status.ACTIVE
                    sub.is_active = True
            elif stripe_status in ["past_due", "unpaid"]:
                sub.status = Subscription.Status.PAST_DUE
                sub.is_active = False
            elif stripe_status == "canceled":
                sub.status = Subscription.Status.CANCELED
                sub.is_active = False
                sub.stripe_subscription_id = ""
            
            sub.save()
            print(f"Subscription updated in Stripe. Status sync: {sub.status} for user: {sub.user.email}")

    return HttpResponse(status=200)