from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Preferences

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')


@admin.register(Preferences)
class PreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "max_appointments", "confirm_manually_appointments")
