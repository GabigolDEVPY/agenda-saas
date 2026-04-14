from django.contrib import admin
from .models import Establishment, OperatingHours


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user', 'cnpj', 'phone', 'description')

@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('establishment', 'day_of_week', 'open_time', 'close_time', 'is_closed')