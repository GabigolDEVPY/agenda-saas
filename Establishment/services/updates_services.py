from establishment.forms import EstablishmentForm, AddressForm
from establishment.models import Establishment, Address
from django.shortcuts import render, get_object_or_404
import json

class UpdateService:
    def __init__(self, request, *args, **kwargs):
        self.request = request

    @staticmethod
    def save_address(request):
        def post(self, request):
            establishment = request.user.owned_establishment
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
                    "message": "Erro ao salvar endereço."
                }
            })
            return response