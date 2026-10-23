from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from billing.services.account_service import AccountService
from establishment.mixins.mixins import OwnerRequiredMixin


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
