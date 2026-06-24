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
        url = StripeService.create_checkout_session(request, plan=plan)
        return redirect(url.url)


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
