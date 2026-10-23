from django.contrib import admin

from billing.models import Plan, Subscription

# Register your models here.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "max_services_per_user", "max_users_per_establishment", "is_active")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date")

