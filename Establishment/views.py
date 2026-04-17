import json
from django.shortcuts import render
from django.views import View
from .services import HomeService
from . models import Establishment
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView
from .forms import EstablishmentForm

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

    def get_object(self, queryset=None):
        uid = self.request.session.get("uid")
        return Establishment.objects.get(uid=uid)

    def _build_error_message(self, form):
        mensagens = []

        for field, errors in form.errors.items():
            if field == "__all__":
                mensagens.extend([str(e) for e in errors])
            else:
                label = form.fields[field].label or field
                mensagens.extend([f"{label}: {e}" for e in errors])

        return " | ".join(mensagens) if mensagens else "Verifique os dados do formulário."

    def form_valid(self, form):
        self.object = form.save()

        response = render(
            self.request,
            self.template_name,
            {"establishment": self.object, "form": form},
        )
        response["HX-Trigger"] = json.dumps({
            "notify": {
                "type": "success",
                "message": "Informações salvas com sucesso!"
            }
        })
        return response

    def form_invalid(self, form):
        self.object = self.get_object()

        response = render(
            self.request,
            self.template_name,
            {"establishment": self.object, "form": form},
            status=400,
        )
        response["HX-Trigger"] = json.dumps({
            "notify": {
                "type": "error",
                "message": self._build_error_message(form)
            }
        })
        return response
    


class SaveAddressView(UpdateView):
    model = Establishment
    fields = ['cep', 'cidade', 'estado', 'bairro', 'rua', 'numero_endereco', 'complemento']
    
    def get_object(self, queryset=None):
        uid = self.request.session.get('uid')
        return Establishment.objects.get(uid=uid)
    
    def form_valid(self, form):
        self.object.save()
        return render(self.request, 'partials/address.html', context={'establishment': self.object})
    