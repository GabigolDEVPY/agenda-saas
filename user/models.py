from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    establishment = models.ForeignKey(
        "establishment.Establishment",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    is_owner = models.BooleanField(default=False)

    def get_display_name(self):
        name = self.get_full_name().strip()
        return name if name else self.username

    def __str__(self):
        return self.username
    
class Preferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")
    max_appointments = models.IntegerField(default=8)
    confirm_manually_appointments = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"
    

