from establishment.forms import EstablishmentForm, AddressForm
from establishment.models import Establishment, Address
from django.shortcuts import render, get_object_or_404
import json

class UpdateService:

    @staticmethod
    def save_address(request):
        establishment = request.user.owned_establishment
        address_instance = Address.objects.filter(establishment=establishment).first()

        form = AddressForm(request.POST, instance=address_instance)

        if form.is_valid():
            address = form.save(commit=False)
            address.establishment = establishment
            address.save()
            return True, form, address

        return False, form, address_instance