from django.contrib import admin
from .models import Service, Appointment, MonthAvailability, HoursUnavailable, Diverses


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'time_duration', 'user')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'time', 'date', 'user', 'service', 'total', 'duration')


@admin.register(MonthAvailability)
class MonthAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'availability')


@admin.register(HoursUnavailable)
class HoursUnavailableAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'day', 'hour', 'availability')


@admin.register(Diverses)
class DiversesAdmin(admin.ModelAdmin):
    list_display = ('user', 'interval_time', 'descricao')