import json
from django.shortcuts import render
from django.views import View
from .forms import EstablishmentForm, AddressForm, OperatingHoursForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.services import OperationDayService, GerenalPreferencesService
from django.http import JsonResponse
from django.db import transaction
from .mixins.mixins import OwnerRequiredMixin




class SaveInfosView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request):
        establishment = request.user.owned_establishment

        if request.method == "POST":
            form = EstablishmentForm(request.POST, instance=establishment)

            if form.is_valid():
                establishment = form.save()
                form = EstablishmentForm(instance=establishment)
                return render(request, "partials/establishment/infos.html", {"establishment": establishment, "form": form})
            else:
                return render(request, "partials/establishment/infos.html", {"establishment": establishment, "form": form})
        return self.request.user.owned_establishment




class SaveAddressView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request):
        address = request.user.owned_establishment.address

        if request.method == "POST":
            form = AddressForm(request.POST, instance=address)

            if form.is_valid():
                address = form.save(commit=False)
                address.completed = True
                address.save()
                form = AddressForm(instance=address)
                return render(request, "partials/establishment/address.html", {"address": address, "form": form})
            else:
                return render(request, "partials/establishment/address.html", {"address": address, "form": form})




class SaveOperatingHoursView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request):
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"status": "error", "message": "Invalid JSON data."})
        else:
            data = request.POST

        form = OperatingHoursForm(data=data)

        if not form.is_valid():
            return JsonResponse({"status": "error", "message": form.errors})

        with transaction.atomic():
            result = OperationDayService.update_operating_hours(clean_data=form.cleaned_data, user=request.user)
        return JsonResponse(result)
    


class GeneralPreferencesView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def post(self, request):
        try:
            if request.content_type == "application/json":
                data = json.loads(request.body)
            else:
                data = {
                    "field": request.POST.get("field"),
                    "value": request.POST.get("value") == "true",
                }
            prefs = request.user.establishment.general_preferences
            GerenalPreferencesService.update_general_preferences(prefs=prefs, data=data)

            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/establishment/general_preferences.html",
                    {"gereral_preferences": prefs},
                )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
