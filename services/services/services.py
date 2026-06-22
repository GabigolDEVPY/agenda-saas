from django.http import Http404
from django.shortcuts import get_object_or_404
from services.forms import ServiceForm
from services.models import Service


class ServiceService:
    @staticmethod
    def get_establishment(user):
        if getattr(user, "is_owner", False):
            establishment = getattr(user, "owned_establishment", None)
            if establishment:
                return establishment

        return getattr(user, "establishment", None)

    @staticmethod
    def get_service_users(user, establishment=None):
        if establishment is None:
            establishment = ServiceService.get_establishment(user)

        if getattr(user, "is_owner", False) and establishment:
            return user.__class__.objects.filter(establishment=establishment)

        return user.__class__.objects.filter(pk=user.pk)

    @staticmethod
    def get_services(user, service_users=None):
        users = service_users if service_users is not None else ServiceService.get_service_users(user)

        return (
            Service.objects.filter(user__in=users)
            .select_related("user")
            .order_by(
                "user__first_name",
                "user__last_name",
                "name",
            )
        )

    @staticmethod
    def get_service(user, pk):
        if not pk:
            raise Http404("Servico nao encontrado.")

        return get_object_or_404(ServiceService.get_services(user), pk=pk)

    @staticmethod
    def get_form(user, data=None, instance=None, users=None):
        return ServiceForm(data=data, instance=instance)

    @staticmethod
    def create_service(user, data):
        form = ServiceService.get_form(user, data=data)

        if not form.is_valid():
            return None, form, False

        service = form.save(commit=False)
        service.user = user
        service.save()
        return service, form, True

    @staticmethod
    def update_service(user, pk, data):
        service = ServiceService.get_service(user, pk)
        form = ServiceService.get_form(user, data=data, instance=service)

        if not form.is_valid():
            return service, form, False

        service = form.save()
        return service, form, True

    @staticmethod
    def delete_service(user, pk):
        service = ServiceService.get_service(user, pk)
        service.delete()
        return service
