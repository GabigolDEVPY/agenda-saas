import uuid
from django.db import models


class Establishment(models.Model):
    user = models.OneToOneField("user.User", on_delete=models.CASCADE, related_name="owned_establishment")
    name = models.CharField(max_length=255)
    uid = models.CharField(max_length=20, unique=True, editable=False)
    cnpj = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=15)
    description = models.TextField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    
class OperatingHours(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="operating_hours")
    day_of_week = models.IntegerField(choices=[(i, d) for i, d in enumerate(['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'])])
    open_time = models.TimeField()
    close_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('establishment', 'day_of_week')

    def __str__(self):
        return f"{self.establishment.name} - {self.get_day_of_week_display()}: {self.open_time} - {self.close_time}"