from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from establishment.mixins.mixins import OwnerRequiredMixin


class CheckoutView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages.info(
            request,
            "Checkout ainda nao configurado. Integre o provedor de pagamento nesta rota.",
        )
        return redirect(f"{reverse('admin_portal:home')}?tab=plano")
