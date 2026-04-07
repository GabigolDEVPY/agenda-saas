from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    establishment = models.ForeignKey(
        "Establishment.Establishment",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.username