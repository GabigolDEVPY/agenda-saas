from django.conf import settings
from django.db import models
from django.utils import timezone


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True, default="Plano Inicial")
    max_services_per_user = models.PositiveIntegerField(default=30)
    max_users_per_establishment = models.PositiveIntegerField(default=5)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_price_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Ativa"
        PENDING = "pending", "Pendente"
        CANCELED = "canceled", "Cancelada"
        EXPIRED = "expired", "Expirada"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    start_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    @property
    def can_use_public_agenda(self):
        if not self.is_active or self.status != self.Status.ACTIVE:
            return False

        if self.expires_at and self.expires_at <= timezone.now():
            return False

        return self.plan.is_active

    def __str__(self):
        return f"{self.user} - {self.plan}"
