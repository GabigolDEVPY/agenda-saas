from django.db import models
from Establishment.models import Establishment

# Create your models here.
class Employee(models.Model):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name