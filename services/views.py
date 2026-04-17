import json
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from .services import AppointmentService
from establishment.models import Establishment, Address
from establishment.forms import build_operating_hours_formset
from django.contrib import messages


def order_operating_hours_forms(formset):
    order_map = {6: 0, 0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6}

    def _day(form):
        try:
            return int(form["day_of_week"].value())
        except (TypeError, ValueError):
            return 99

    return sorted(formset.forms, key=lambda form: order_map.get(_day(form), 99))


class ServicesView(LoginRequiredMixin, TemplateView):
    template_name = "admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        establishment = getattr(self.request.user, "owned_establishment", None)
        session_uid = self.request.session.get("uid")

        if establishment and (not session_uid or session_uid != establishment.uid):
            self.request.session["uid"] = establishment.uid

        context["establishment"] = establishment
        context["address"] = Address.objects.filter(establishment=establishment).first() if establishment else None
        if establishment:
            formset = build_operating_hours_formset(establishment)
            context["operating_hours_formset"] = formset
            context["operating_hours_forms"] = order_operating_hours_forms(formset)
        else:
            context["operating_hours_formset"] = None
            context["operating_hours_forms"] = None
        return context


class CreateAppointmentView(View):
    def post(self, request):
        errors, result = AppointmentService.create_appointment(request.POST)

        if not result:
            messages.error(request, json.dumps({"status": "error", "title": "Erro de validacao", "message": str(errors)}))
            return redirect(request.META.get("HTTP_REFERER"))

        if result and result.get("status") == "success":
            uid = result["uid"]
            messages.success(
                request,
                json.dumps(
                    {
                        "status": result["status"],
                        "horario": result["horario"],
                        "title": result["title"],
                        "message": result["message"],
                    }
                ),
            )

        elif result:
            uid = result["uid"]
            messages.error(
                request,
                json.dumps({"status": result["status"], "title": result["title"], "message": result["message"]}),
            )

        return redirect("establishment:public_agenda", uid=uid)
