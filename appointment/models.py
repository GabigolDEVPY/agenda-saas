from django.db import models
from django.conf import settings
from services.models import Service




class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        REJECTED = 'rejected', 'Recusado'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(help_text="Duração em minutos")
    client_name = models.CharField(max_length=40)
    phone = models.CharField(max_length=15)
    observation = models.TextField(blank=True, null=True, max_length=100)
    total = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return f"{self.client_name} - {self.date} {self.time}"


class MonthAvailability(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='month_availability',
    )
    year = models.IntegerField()
    month = models.IntegerField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.month} - {'Disponível' if self.availability else 'Indisponível'}"


class DayUnavailable(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    month = models.ForeignKey(MonthAvailability, on_delete=models.CASCADE)
    day = models.IntegerField()

    class Meta:
        unique_together = ('user', 'month', 'day')

    def __str__(self):
        return f"{self.user} - {self.month.month}/{self.month.year}/{self.day} - Dia indisponível"


class HoursUnavailable(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    month = models.ForeignKey(MonthAvailability, on_delete=models.CASCADE)
    day = models.IntegerField()
    hour = models.TimeField()

    class Meta:
        unique_together = ('user', 'month', 'day', 'hour')

    def __str__(self):
        return f"{self.user} - {self.month.month}/{self.month.year}/{self.day} {self.hour} - Indisponível"

