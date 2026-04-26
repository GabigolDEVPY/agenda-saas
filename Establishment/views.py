import json
from django.shortcuts import render
from django.views import View
from .services.services import HomeService
from . models import Establishment, Address
from  . exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
from django.views.generic import UpdateView
from .forms import EstablishmentForm, AddressForm, OperatingHoursForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.form_services import get_msg_form_invalid
from .services.operation_day_service import OperationDayService
from django.http import JsonResponse



class PublicAgenda(View):
    def get(self, request, uid):
        context = HomeService.get_context_establishment(uid)
        request.session['uid'] = uid  
        if context.get("incomplete") == "True":
            return render(request, 'unavailable.html', context=context)  
        return render(request, 'home.html', context=context)
    


class SaveInfosView(LoginRequiredMixin, UpdateView):
    model = Establishment
    form_class = EstablishmentForm
    template_name = "partials/infos.html"

    def get_object(self):
        return self.request.user.owned_establishment

    def form_valid(self, form):
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


# api view para atualizar horários de funcionamento
class SaveOperatingHoursView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)

        form = OperatingHoursForm(data=data)

        if not form.is_valid():
            return JsonResponse({"status": "error", "message": form.errors})

        result = OperationDayService.update_operating_hours(clean_data=form.cleaned_data, user=request.user)
        return JsonResponse(result)