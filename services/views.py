from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .services import ServiceService


class ServiceBaseView(LoginRequiredMixin, View):
    list_template_name = "partials/services/list.html"

    def get_services(self):
        return ServiceService.get_services(self.request.user)

    def get_service(self, pk=None):
        service_id = pk or self.request.POST.get("service_id")
        return ServiceService.get_service(self.request.user, service_id)

    def get_form(self, data=None, instance=None):
        return ServiceService.get_form(self.request.user, data=data, instance=instance)

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
        _service, form, created = ServiceService.create_service(request.user, request.POST)

        if created:
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
        service, form, updated = ServiceService.update_service(request.user, pk, request.POST)

        if updated:
            if request.headers.get("HX-Request"):
                return self.render_modal(service, updated=True)

            return redirect(self.home_url())

        if request.headers.get("HX-Request"):
            return self.render_modal(service, form=form)

        return HttpResponse(status=400)


class ServiceDeleteView(ServiceBaseView):
    def post(self, request, *args, **kwargs):
        ServiceService.delete_service(request.user, request.POST.get("service_id"))

        if request.headers.get("HX-Request"):
            response = self.render_list()
            response["HX-Trigger"] = "serviceDeleted"
            return response

        return redirect(self.home_url())
