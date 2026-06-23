from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from appointment.models import Appointment


class Command(BaseCommand):
    help = (
        "Remove agendamentos confirmados com mais de 90 dias "
        "e cancelados/recusados com mais de 30 dias"
    )

    def handle(self, *args, **kwargs):
        time_now = timezone.now().date()

        limite_confirmed = time_now - timedelta(days=90)
        limite_canceleds = time_now - timedelta(days=30)

        queryset = Appointment.objects.filter(
            Q(
                date__lt=limite_confirmed,
                status=Appointment.Status.CONFIRMED,
            )
            | Q(
                date__lt=limite_canceleds,
                status__in=[
                    Appointment.Status.CANCELED,
                    Appointment.Status.REJECTED,
                ],
            )
        )

        quantidade = queryset.count()

        queryset.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{quantidade} agendamentos removidos com sucesso."
            )
        )
