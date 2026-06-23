from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from billing.services import LimitsService
from .forms import EmployeeCreationForm, EmployeePasswordChangeForm
from .models import Preferences, User
from establishment.mixins.mixins import OwnerRequiredMixin


class EmployeeCreateView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = "partials/employees/create_employee_modal.html"

    def get_establishment(self):
        return getattr(self.request.user, "owned_establishment", None) or self.request.user.establishment

    def get_employees(self):
        return User.objects.filter(
            establishment=self.get_establishment(),
            is_owner=False,
        ).order_by("first_name", "last_name", "username")

    def render_modal(self, form=None, created=False):
        return render(
            self.request,
            self.template_name,
            {
                "employee_form": form or EmployeeCreationForm(),
                "employees": self.get_employees(),
                "limits": LimitsService.context(self.request.user, self.get_establishment()),
                "employee_created": created,
            },
        )

    def post(self, request, *args, **kwargs):
        form = EmployeeCreationForm(request.POST)

        if form.is_valid():
            allowed, message = LimitsService.validate(request.user, LimitsService.FEATURE_USERS)
            if not allowed:
                form.add_error(None, message)
                if request.headers.get("HX-Request"):
                    return self.render_modal(form=form)
                return HttpResponse(status=400)

            employee = form.save(commit=False)
            employee.establishment = self.get_establishment()
            employee.save()
            Preferences.objects.get_or_create(user=employee)

            if request.headers.get("HX-Request"):
                response = self.render_modal(created=True)
                response["HX-Trigger"] = "employeeCreated"
                return response

            return redirect(f"{reverse('admin_portal:home')}?tab=funcionarios")

        if request.headers.get("HX-Request"):
            return self.render_modal(form=form)

        return HttpResponse(status=400)


class EmployeeOwnerBaseView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get_establishment(self):
        return getattr(self.request.user, "owned_establishment", None) or self.request.user.establishment

    def get_employees(self):
        return User.objects.filter(
            establishment=self.get_establishment(),
            is_owner=False,
        ).order_by("first_name", "last_name", "username")

    def get_employee(self):
        employee_id = self.request.POST.get("employee_id")
        return get_object_or_404(
            User,
            id=employee_id,
            establishment=self.get_establishment(),
            is_owner=False,
        )


class EmployeeDeleteView(EmployeeOwnerBaseView):
    template_name = "partials/employees/list.html"

    def post(self, request, *args, **kwargs):
        employee = self.get_employee()
        employee.delete()

        if request.headers.get("HX-Request"):
            response = render(
                request,
                self.template_name,
                {
                    "employees": self.get_employees(),
                    "limits": LimitsService.context(request.user, self.get_establishment()),
                },
            )
            response["HX-Trigger"] = "employeeDeleted"
            return response

        return redirect(f"{reverse('admin_portal:home')}?tab=funcionarios")


class EmployeePasswordChangeView(EmployeeOwnerBaseView):
    template_name = "partials/employees/change_password_modal.html"

    def render_modal(self, employee, form=None, changed=False):
        response = render(
            self.request,
            self.template_name,
            {
                "password_employee": employee,
                "password_form": form or EmployeePasswordChangeForm(employee),
                "password_modal_open": bool(form and form.errors),
            },
        )
        if changed:
            response["HX-Trigger"] = "employeePasswordChanged"
        return response

    def post(self, request, *args, **kwargs):
        employee = self.get_employee()
        form = EmployeePasswordChangeForm(employee, request.POST)

        if form.is_valid():
            form.save()

            if request.headers.get("HX-Request"):
                return self.render_modal(employee, changed=True)

            return redirect(f"{reverse('admin_portal:home')}?tab=funcionarios")

        if request.headers.get("HX-Request"):
            return self.render_modal(employee, form=form)

        return HttpResponse(status=400)
