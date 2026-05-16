import json
from django.shortcuts import render
from django.views import View
from .forms import EstablishmentForm, AddressForm, OperatingHoursForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.form_services import get_msg_form_invalid
from .services.services import OperationDayService, GerenalPreferencesService
from django.http import JsonResponse
from django.db import transaction




class SaveInfosView(LoginRequiredMixin, View):
    def post(self, request):
        establishment = request.user.owned_establishment

        if request.method == "POST":
            form = EstablishmentForm(request.POST, instance=establishment)

            if form.is_valid():
                establishment = form.save()
                return render(request, "partials/infos.html", {"establishment": establishment,"form": form,"msg": "Informações salvas com sucesso!","type": "success"})
            else:
                msg = get_msg_form_invalid(request, form)
                return render(request, "partials/infos.html", {"establishment": establishment,"form": form,"msg": msg,"type": "error"})
        return self.request.user.owned_establishment




class SaveAddressView(LoginRequiredMixin, View):
    def post(self, request):
        address = request.user.owned_establishment.address

        if request.method == "POST":
            form = AddressForm(request.POST, instance=address)

            if form.is_valid():
                address = form.save()
                return render(request, "partials/address.html", {"address": address,"form": form,"msg": "Endereço salvo com sucesso!","type": "success"})
            else:
                msg = get_msg_form_invalid(request, form)
                return render(request, "partials/address.html", {"address": address,"form": form,"msg": msg,"type": "error"})




class SaveOperatingHoursView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data."})

        form = OperatingHoursForm(data=data)

        if not form.is_valid():
            return JsonResponse({"status": "error", "message": form.errors})

        with transaction.atomic():
            result = OperationDayService.update_operating_hours(clean_data=form.cleaned_data, user=request.user)
        return JsonResponse(result)
    


class GeneralPreferencesView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)        
            prefs = request.user.establishment.general_preferences
            result = GerenalPreferencesService.update_general_preferences(prefs=prefs, data=data)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
