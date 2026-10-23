from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.conf import settings
from billing.models import Subscription
from establishment.models import Establishment
import stripe

class AccountService:
    @staticmethod
    def cancel_subscription(user):
        if not user or not user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")
        
        if not user.is_owner:
            raise PermissionDenied("Apenas o proprietário do estabelecimento pode cancelar a assinatura.")
            
        subscription = getattr(user, 'subscription', None)
        if subscription and subscription.stripe_subscription_id:
            stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None) or getattr(settings, 'STRIPE_TOKEN', None)
            stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=True)
            
            subscription.status = Subscription.Status.CANCELED
            # We keep subscription.is_active = True so they can use it until the billing period end (expires_at)
            subscription.save()
            return True
        return False


    @staticmethod
    @transaction.atomic
    def delete_account(request, user):
        """
        Permanently deletes the owner's user account and everything associated with it
        in cascade, then performs logout.
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied("Usuário não autenticado.")
            
        if not user.is_owner:
            raise PermissionDenied("Apenas o proprietário do estabelecimento pode excluir a conta permanentemente.")
            
        # Logging out the user first so their session is cleaned up
        logout(request)
        
        # Deleting the owner user triggers cascade delete for all associated resources:
        # User -> Establishment (OneToOne CASCADE)
        # Establishment -> other Users (employees) (ForeignKey CASCADE)
        # Users -> Preferences, Subscription, Services, Appointments, Availabilities (CASCADE)
        # Establishment -> Address, OperatingHours, GeneralPreference (CASCADE)
        user.delete()
        return True
