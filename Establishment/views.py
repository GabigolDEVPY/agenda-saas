import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from .services.services import HomeService
from . models import Establishment, Address
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView
from .forms import EstablishmentForm, AddressForm
from .services.updates_services import UpdateService

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

    def post(self, request, *args, **kwargs):
        UpdateService.save_address(request)
        return super().post(request, *args, **kwargs)
