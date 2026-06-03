from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from .forms import EmployeeCreationForm
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
                "employee_created": created,
            },
        )

    def post(self, request, *args, **kwargs):
        form = EmployeeCreationForm(request.POST)

        if form.is_valid():
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
