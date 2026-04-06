from django.db import models
from Establishment.models import Establishment
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name='users')
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username

