import json
from django.shortcuts import render
from django.views import View
from .services.services import HomeService
from . models import Establishment, Address
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView
from .forms import EstablishmentForm, AddressForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.form_services import get_msg_form_invalid
from .services.operation_day_service import OperationDayService
from django.http import JsonResponse

class PublicAgenda(View):
    def get(self, request, uid):
        try:
            context = HomeService.get_context_establishment(uid)
            request.session['uid'] = uid  
        except EstablishmentNotFound:
            context = {"msg": "Estabelecimento não encontrado. Verifique o link ou entre em contato com o estabelecimento para mais informações."}
            return render(request, 'unavailable.html', context=context)  
        
        except EstablishmentIncomplete:
            context = {"msg": "Configurações incompletas. Entre em contato com o estabelecimento para mais informações.", "incomplete": True}
            return render(request, 'unavailable.html', context=context)  
        
        except EstablishmentInactive:
            context = {"msg": "Estabelecimento inativo. Entre em contato com o estabelecimento para mais informações.", "payment": True}
            return render(request, 'unavailable.html', context=context)

        return render(request, 'home.html', context=context)
    


class SaveInfosView(LoginRequiredMixin, UpdateView):
    model = Establishment
    form_class = EstablishmentForm
    template_name = "partials/infos.html"

    def get_object(self):
        return self.request.user.owned_establishment

    def form_valid(self, form):
        print(self.request.user.owned_establishment.__dict__)
        establishment = form.save()
        response = render(self.request, self.template_name, {"establishment": establishment, "form": form, "msg": "Informações salvas com sucesso!", "type": "success"})
        return response

    def form_invalid(self, form):
        msg = get_msg_form_invalid(self, form)
        response = render( self.request, self.template_name, {"establishment": self.get_object(), "form": form, "msg": msg, "type": "error"})
        return response
    


class SaveAddressView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = "partials/address.html"

    def get_object(self):
        return self.request.user.owned_establishment.address

    def form_valid(self, form):
        address = form.save()
        response = render(self.request, self.template_name, {"address": address, "form": form, "msg": "Endereço salvo com sucesso!", "type": "success"})
        return response

    def form_invalid(self, form):
        msg = get_msg_form_invalid(self, form)
        response = render( self.request, self.template_name, {"address": self.get_object(), "form": form, "msg": msg, "type": "error"})
        return response 





class SaveOperatingHoursView(LoginRequiredMixin, View):
    def post(self, request):
        print(request.body)
        result = OperationDayService.update_operating_hours(day=request.body)
        # Lógica para salvar os horários de funcionamento
        # Você pode acessar os dados enviados via request.POST ou request.body
        # e atualizar o modelo de horários de funcionamento do estabelecimento
        return JsonResponse({"status": "success", "message": "Horários de funcionamento atualizados com sucesso!"})