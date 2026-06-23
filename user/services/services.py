from establishment.models import OperatingHours, GeneralPreference, Address
from datetime import time
from django.db import transaction
from billing.models import Subscription
from billing.services import LimitsService

class UserServices:
    @staticmethod
    @transaction.atomic 
    def create_data_establishment(user):
        establishment = user.establishment

        # criando as preferências gerais
        GeneralPreference.objects.create(
            establishment=establishment,
            open_establishment=True,
            show_phone_publicly=True
            )

        days = range(7)

        # criando os dias de agenda
        for day in days:
            OperatingHours.objects.create(
                establishment=establishment,
                day_of_week=day,
                open_time=time(6, 0),
                close_time=time(18, 0),
                is_closed=True
            )
        # criando o endereço
        Address.objects.create(
            establishment=establishment,
        )

        Subscription.objects.get_or_create(
            user=user,
            defaults={"plan": LimitsService.get_default_plan()},
        )

        return
