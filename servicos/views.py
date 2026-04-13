import json
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from .services import AppointmentService
from django.contrib import messages

class ServicosView(LoginRequiredMixin, TemplateView):

    template_name = 'admin.html'


class CreateAppointmentView(View):
    def post(self, request):
        errors, result = AppointmentService.create_appointment(request.POST)

        if not result:
            messages.error(request, json.dumps({
                "status": "error",
                "title": "Erro de validação",
                "message": str(errors)
            }))
            return redirect(request.META.get("HTTP_REFERER"))

        if result and result.get("status") == "success":
            uid = result["uid"]
            messages.success(request, json.dumps({
                "status": result["status"],
                "horario": result["horario"],
                "title": result["title"],
                "message": result["message"]
            }))

        elif result:
            uid = result["uid"]
            messages.error(request, json.dumps({
                "status": result["status"],
                "title": result["title"],
                "message": result["message"]
            }))

        return redirect("establishment:public_agenda", uid=uid)