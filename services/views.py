from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import ServiceForm
from .models import Service


class ServiceBaseView(LoginRequiredMixin, View):
    list_template_name = "partials/services/list.html"

    def get_establishment(self):
        return (
            getattr(self.request.user, "owned_establishment", None)
            or self.request.user.establishment
        )

    def get_service_users(self):
        establishment = self.get_establishment()
        if self.request.user.is_owner and establishment:
            return establishment.users.order_by("first_name", "last_name", "username")
        return self.request.user.__class__.objects.filter(pk=self.request.user.pk)

    def get_services(self):
        return Service.objects.filter(user__in=self.get_service_users()).select_related("user").order_by(
            "user__first_name",
            "user__last_name",
            "name",
        )

    def get_service(self, pk=None):
        if pk is None:
            pk = self.request.POST.get("service_id")
        return get_object_or_404(Service, pk=pk, user__in=self.get_service_users())

    def get_form(self, data=None, instance=None):
        return ServiceForm(data=data, instance=instance, users=self.get_service_users())

    def render_list(self, **context):
        return render(
            self.request,
            self.list_template_name,
            {"services": self.get_services(), **context},
        )

    def home_url(self):
        return f"{reverse('admin_portal:home')}?tab=servicos"


class ServiceCreateView(ServiceBaseView):
    template_name = "partials/services/new_service.html"

    def render_modal(self, form=None, created=False):
        return render(
            self.request,
            self.template_name,
            {
                "service_form": form or self.get_form(),
                "services": self.get_services(),
                "service_created": created,
            },
        )

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST)

        if form.is_valid():
            form.save()

            if request.headers.get("HX-Request"):
                response = self.render_modal(created=True)
                response["HX-Trigger"] = "serviceCreated"
                return response

            return redirect(self.home_url())

        if request.headers.get("HX-Request"):
            return self.render_modal(form=form)

        return HttpResponse(status=400)


class ServiceEditFormView(ServiceBaseView):
    template_name = "partials/services/edit_service.html"

    def get(self, request, pk, *args, **kwargs):
        service = self.get_service(pk)
        return render(
            request,
            self.template_name,
            {
                "service": service,
                "service_form": self.get_form(instance=service),
                "service_modal_open": True,
            },
        )


class ServiceUpdateView(ServiceBaseView):
    template_name = "partials/services/edit_service.html"

    def render_modal(self, service, form=None, updated=False):
        response = render(
            self.request,
            self.template_name,
            {
                "service": service,
                "service_form": form or self.get_form(instance=service),
                "services": self.get_services(),
                "service_modal_open": bool(form and form.errors),
                "service_updated": updated,
            },
        )
        if updated:
            response["HX-Trigger"] = "serviceUpdated"
        return response

    def post(self, request, pk, *args, **kwargs):
        service = self.get_service(pk)
        form = self.get_form(data=request.POST, instance=service)

        if form.is_valid():
            service = form.save()

            if request.headers.get("HX-Request"):
                return self.render_modal(service, updated=True)

            return redirect(self.home_url())

        if request.headers.get("HX-Request"):
            return self.render_modal(service, form=form)

        return HttpResponse(status=400)


class ServiceDeleteView(ServiceBaseView):
    def post(self, request, *args, **kwargs):
        service = self.get_service()
        service.delete()

        if request.headers.get("HX-Request"):
            response = self.render_list()
            response["HX-Trigger"] = "serviceDeleted"
            return response

        return redirect(self.home_url())
