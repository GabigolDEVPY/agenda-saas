from django.db import models
from django.conf import settings


class Service(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
    )
    name = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    time_duration = models.IntegerField(help_text="Duração em minutos")

    def __str__(self):
        return self.name


class Appointment(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

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


class HoursUnavailable(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    month = models.ForeignKey(MonthAvailability, on_delete=models.CASCADE)
    day = models.IntegerField()
    hour = models.TimeField()
    availability = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"{self.user} - {self.month.month}/{self.month.year}/{self.day} "
            f"{self.hour} - {'Disponível' if self.availability else 'Indisponível'}"
        )


class Diverses(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    interval_time = models.IntegerField(
        default=30, help_text="Intervalo entre horários em minutos"
    )
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Intervalo: {self.interval_time} minutos"