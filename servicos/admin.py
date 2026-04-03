from django.contrib import admin
from .models import Service, Appointment, MonthAvailability, HoursUnavailable, Diverses

# Register your models here.

@admin.register(Service)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'time_duration')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'time', 'date', 'employee', 'service', 'total' , 'duration')

@admin.register(MonthAvailability)
class MonthAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'availability')

@admin.register(HoursUnavailable)
class HoursUnavailableAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'day', 'hour', 'availability')

@admin.register(Diverses)
class DiversesAdmin(admin.ModelAdmin):
    list_display = ('interval_time', 'descricao')