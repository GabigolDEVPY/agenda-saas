from establishment.models import OperatingHours, Establishment
from datetime import time
from django.db import transaction

class UserServices:
    @staticmethod
    @transaction.atomic 
    def create_operation_hours(form):
        user = form.save()
        establishment = user.establishment
        days = range(7)
        for day in days:
            OperatingHours.objects.create(
                establishment=establishment,
                day_of_week=day,
                open_time=(6, 0),
                close_time=(18, 0),
                is_closed=True
            )
        return