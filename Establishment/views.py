from django.shortcuts import render
from django.views import View
from .services import HomeService
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete

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