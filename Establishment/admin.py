from django.contrib import admin
from . models import Establishment
# Register your models here.

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user')