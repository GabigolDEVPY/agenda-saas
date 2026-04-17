import json
from django.shortcuts import render, get_object_or_404
from django.views import View
from .services import HomeService
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
    


class SaveAddressView(View):
    template_name = "partials/address.html"

    def _get_establishment(self):
        uid = self.request.session.get("uid")
        return get_object_or_404(Establishment, uid=uid)

    def _build_error_message(self, form):
        mensagens = []

        for field, errors in form.errors.items():
            if field == "__all__":
                mensagens.extend([str(e) for e in errors])
            else:
                label = form.fields[field].label or field
                mensagens.extend([f"{label}: {e}" for e in errors])

        return " | ".join(mensagens) if mensagens else "Verifique os dados do formulário."

    def post(self, request, *args, **kwargs):
        establishment = self._get_establishment()
        address_instance = Address.objects.filter(establishment=establishment).first()

        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.establishment = establishment
            address.save()

            response = render(
                request,
                self.template_name,
                {"establishment": establishment, "address": address, "form": form},
            )
            response["HX-Trigger"] = json.dumps({
                "notify": {
                    "type": "success",
                    "message": "Endereço salvo com sucesso!"
                }
            })
            return response

        response = render(
            request,
            self.template_name,
            {"establishment": establishment, "address": address_instance, "form": form},
            status=400,
        )
        response["HX-Trigger"] = json.dumps({
            "notify": {
                "type": "error",
                "message": self._build_error_message(form)
            }
        })
        return response
    
