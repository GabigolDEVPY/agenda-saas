from establishment.models import OperatingHours, Establishment, GeneralPreference, Address
from datetime import time
from django.db import transaction

class UserServices:
    @staticmethod
    @transaction.atomic 
    def create_data_establishment(user):
        establishment = user.establishment
        print("criando general preference")
        GeneralPreference.objects.create(
            establishment=establishment,
            open_establishment=True,
            show_phone_publicly=True
            )

        days = range(7)

        for day in days:
            OperatingHours.objects.create(
                establishment=establishment,
                day_of_week=day,
                open_time=time(6, 0),
                close_time=time(18, 0),
                is_closed=True
            )
        Address.objects.create(
            establishment=establishment,
        )

        return