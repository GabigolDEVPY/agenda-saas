from django.contrib import admin
from .models import Appointment, MonthAvailability, HoursUnavailable, DayUnavailable


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'time', 'date', 'user', 'service', 'status', 'total', 'duration')


@admin.register(MonthAvailability)
class MonthAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'availability')


@admin.register(DayUnavailable)
class DayUnavailableAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'day')


@admin.register(HoursUnavailable)
class HoursUnavailableAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'day', 'hour')


