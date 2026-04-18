import json
from django.shortcuts import render
from django.views import View
from .services.services import HomeService
from . models import Establishment, Address
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView
from .forms import EstablishmentForm, AddressForm

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
    


class SaveInfosView(UpdateView):
    model = Establishment
    form_class = EstablishmentForm
    template_name = "partials/infos.html"

    def get_object(self):
        return self.request.user.owned_establishment

    def form_valid(self, form):
        establishment = form.save()
        response = render(self.request, self.template_name, {"establishment": establishment, "form": form},)
        response["HX-Trigger"] = json.dumps({ "notify": {"type": "success","message": "Informações salvas com sucesso!"}})
        return response

    def form_invalid(self, form):
        response = render( self.request, self.template_name, {"establishment": self.get_object(), "form": form}, status=400,)
        response["HX-Trigger"] = json.dumps({"notify": {"type": "error","message": "Erro ao salvar. Verifique os dados."}})
        return response
    


class SaveAddressView(UpdateView):
    model = Address
    form_class = AddressForm
    template_name = "partials/address.html"

    def get_object(self):
        return self.request.user.owned_establishment.address

    def form_valid(self, form):
        address = form.save()
        response = render(self.request, self.template_name, {"address": address, "form": form},)
        response["HX-Trigger"] = json.dumps({ "notify": {"type": "success","message": "Endereço salvo com sucesso!"}})
        return response

    def form_invalid(self, form):
        response = render( self.request, self.template_name, {"address": self.get_object(), "form": form}, status=400,)
        response["HX-Trigger"] = json.dumps({"notify": {"type": "error","message": "Erro ao salvar endereço."}})
        return response 
