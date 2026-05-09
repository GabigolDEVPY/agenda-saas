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