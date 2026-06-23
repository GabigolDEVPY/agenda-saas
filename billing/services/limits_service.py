from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from billing.models import Plan, Subscription
from services.models import Service


class LimitsService:
    FEATURE_SERVICES = "services"
    FEATURE_USERS = "users"

    DEFAULT_PLAN = {
        "name": "Plano Inicial",
        "max_services_per_user": 30,
        "max_users_per_establishment": 5,
        "price": 0,
        "is_active": True,
    }

    @classmethod
    def get_default_plan(cls):
        plan, _ = Plan.objects.get_or_create(
            name=cls.DEFAULT_PLAN["name"],
            defaults={
                "max_services_per_user": cls.DEFAULT_PLAN["max_services_per_user"],
                "max_users_per_establishment": cls.DEFAULT_PLAN["max_users_per_establishment"],
                "price": cls.DEFAULT_PLAN["price"],
                "is_active": cls.DEFAULT_PLAN["is_active"],
            },
        )
        return plan

    @staticmethod
    def get_establishment(user):
        if not user or not getattr(user, "is_authenticated", False):
            return None

        if getattr(user, "is_owner", False):
            try:
                establishment = user.owned_establishment
            except ObjectDoesNotExist:
                establishment = None

            if establishment:
                return establishment

        return getattr(user, "establishment", None)

    @staticmethod
    def get_owner(establishment):
        return getattr(establishment, "user", None) if establishment else None

    @classmethod
    def get_subscription(cls, user):
        establishment = cls.get_establishment(user)
        owner = cls.get_owner(establishment) or user

        if not owner or not getattr(owner, "is_authenticated", False):
            return None

        subscription, _ = Subscription.objects.get_or_create(
            user=owner,
            defaults={"plan": cls.get_default_plan()},
        )
        return subscription

    @classmethod
    def services_summary(cls, user):
        subscription = cls.get_subscription(user)
        maximum = subscription.plan.max_services_per_user if subscription else cls.DEFAULT_PLAN["max_services_per_user"]
        current = Service.objects.filter(user=user).count()

        return {
            "current": current,
            "maximum": maximum,
            "remaining": max(maximum - current, 0),
            "is_exceeded": current > maximum,
            "is_full": current >= maximum,
            "label": f"{current}/{maximum}",
        }

    @classmethod
    def users_summary(cls, user, establishment=None):
        establishment = establishment or cls.get_establishment(user)
        subscription = cls.get_subscription(user)
        maximum_users = subscription.plan.max_users_per_establishment if subscription else cls.DEFAULT_PLAN["max_users_per_establishment"]
        current_users = establishment.users.count() if establishment else 0
        maximum_employees = max(maximum_users - 1, 0)
        current_employees = establishment.users.filter(is_owner=False).count() if establishment else 0

        return {
            "current": current_users,
            "maximum": maximum_users,
            "remaining": max(maximum_users - current_users, 0),
            "is_exceeded": current_users > maximum_users,
            "is_full": current_users >= maximum_users,
            "employees_current": current_employees,
            "employees_maximum": maximum_employees,
            "employees_remaining": max(maximum_employees - current_employees, 0),
            "employees_label": f"{current_employees}/{maximum_employees}",
            "label": f"{current_users}/{maximum_users}",
        }

    @classmethod
    def validate(cls, user, feature):
        if feature == cls.FEATURE_SERVICES:
            summary = cls.services_summary(user)
            if summary["is_full"]:
                return False, "Voce atingiu o limite de servicos deste profissional."
            return True, None

        if feature == cls.FEATURE_USERS:
            summary = cls.users_summary(user)
            if summary["is_full"]:
                return False, "Voce atingiu o limite de usuarios do estabelecimento."
            return True, None

        raise ValueError(f"Limite desconhecido: {feature}")

    @classmethod
    def has_exceeded_limits(cls, establishment):
        if not establishment:
            return True

        owner = cls.get_owner(establishment)
        users_summary = cls.users_summary(owner, establishment)
        if users_summary["is_exceeded"]:
            return True

        subscription = cls.get_subscription(owner)
        max_services = subscription.plan.max_services_per_user if subscription else cls.DEFAULT_PLAN["max_services_per_user"]
        return (
            Service.objects
            .filter(user__establishment=establishment)
            .values("user_id")
            .annotate(total=Count("id"))
            .filter(total__gt=max_services)
            .exists()
        )

    @classmethod
    def public_agenda_status(cls, establishment):
        owner = cls.get_owner(establishment)
        subscription = cls.get_subscription(owner) if owner else None

        if not subscription or not subscription.can_use_public_agenda:
            return False, "Agenda indisponivel. O plano do estabelecimento nao esta ativo."

        if cls.has_exceeded_limits(establishment):
            return False, "Agenda indisponivel. O estabelecimento excedeu os limites do plano."

        return True, None

    @classmethod
    def context(cls, user, establishment=None):
        subscription = cls.get_subscription(user)
        return {
            "subscription": subscription,
            "services": cls.services_summary(user),
            "users": cls.users_summary(user, establishment),
        }
