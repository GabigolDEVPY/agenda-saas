from django.shortcuts import render
from django.views import View
from .services import HomeService
from . models import Establishment
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView

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
    fields = ['name', 'description', 'phone', 'cnpj']
    
    def get_object(self, queryset=None):
        uid = self.request.session.get('uid')
        return Establishment.objects.get(uid=uid)
    
    def form_valid(self, form):
        self.object.save()
        return render(self.request, 'partials/infos.html', context={'establishment': self.object})
    

class SaveAddressView(UpdateView):
    model = Establishment
    fields = ['cep', 'cidade', 'estado', 'bairro', 'rua', 'numero_endereco', 'complemento']
    
    def get_object(self, queryset=None):
        uid = self.request.session.get('uid')
        return Establishment.objects.get(uid=uid)
    
    def form_valid(self, form):
        self.object.save()
        return render(self.request, 'partials/address.html', context={'establishment': self.object})
    