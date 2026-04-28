from django.contrib import admin
from .models import Establishment, OperatingHours, Address, GeneralPreference


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user', 'cnpj', 'phone', 'description')

@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'day_of_week', 'open_time', 'close_time', 'is_closed')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'street', 'number', 'complement', 'neighborhood', 'city', 'state', 'zip_code')

@admin.register(GeneralPreference)
class GeneralPreferenceAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'show_address_publicly', 'show_phone_publicly')