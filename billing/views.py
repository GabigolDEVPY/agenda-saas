from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from .services.stripe_service import StripeService
from establishment.mixins.mixins import OwnerRequiredMixin
from billing.services.account_service import AccountService
from .models import Plan, Subscription


class CheckoutView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        plan = Plan.objects.filter(name="Plano Inicial").first()
        if not plan or not plan.stripe_price_id:
            messages.error(request, "O plano de pagamento não está configurado corretamente no banco de dados. Entre em contato com o suporte.")
            return redirect(f"{reverse('admin_portal:home')}?tab=conta")
            
        try:
            session = StripeService.create_checkout_session(request, plan=plan)
            return redirect(session.url)
        except Exception as e:
            messages.error(request, f"Erro ao iniciar o pagamento com a Stripe: {str(e)}")
            return redirect(f"{reverse('admin_portal:home')}?tab=conta")


class StripePortalView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        subscription = getattr(request.user, 'subscription', None)
        if subscription and subscription.stripe_customer_id:
            try:
                portal_session = StripeService.create_portal_session(request, subscription.stripe_customer_id)
                return redirect(portal_session.url)
            except Exception as e:
                messages.error(request, f"Erro ao abrir o portal de faturamento: {str(e)}")
        else:
            messages.warning(request, "Nenhuma assinatura com cliente Stripe cadastrado foi encontrada.")
            
        return redirect(f"{reverse('admin_portal:home')}?tab=conta")


class CancelSubscriptionView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            success = AccountService.cancel_subscription(request.user)
            if success:
                messages.success(request, "Sua assinatura foi cancelada com sucesso.")
            else:
                messages.warning(request, "Nenhuma assinatura ativa encontrada para cancelamento.")
        except Exception as e:
            messages.error(request, f"Erro ao cancelar assinatura: {str(e)}")
            
        return redirect(f"{reverse('admin_portal:home')}?tab=conta")


class DeleteAccountView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        confirmation = request.POST.get("confirmation")
        if confirmation != "EXCLUIR":
            messages.error(request, "Confirmação incorreta. Você deve digitar 'EXCLUIR' para prosseguir.")
            return redirect(f"{reverse('admin_portal:home')}?tab=conta")
            
        try:
            AccountService.delete_account(request, request.user)
            messages.success(request, "Sua conta e todos os dados associados foram permanentemente excluídos.")
            return redirect(reverse("user:login"))
        except Exception as e:
            messages.error(request, f"Erro ao excluir conta: {str(e)}")
            return redirect(f"{reverse('admin_portal:home')}?tab=conta")
