from django.contrib import admin
from .models import Establishment


@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user')