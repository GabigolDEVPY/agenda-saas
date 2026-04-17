import json
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from .services import AppointmentService
from establishment.models import Establishment, Address
from django.contrib import messages

class ServicesView(LoginRequiredMixin, TemplateView):
    template_name = 'admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uid = self.request.session.get('uid')
        establishment = Establishment.objects.filter(uid=uid).first()
        context['establishment'] = establishment
        context['address'] = Address.objects.filter(establishment=establishment).first() if establishment else None
        return context


class CreateAppointmentView(View):
    def post(self, request):
        errors, result = AppointmentService.create_appointment(request.POST)

        if not result:
            messages.error(request, json.dumps({"status": "error","title": "Erro de validação","message": str(errors) }))
            return redirect(request.META.get("HTTP_REFERER"))

        if result and result.get("status") == "success":
            uid = result["uid"]
            messages.success(request, json.dumps({"status": result["status"],"horario": result["horario"],"title": result["title"],"message": result["message"]}))

        elif result:
            uid = result["uid"]
            messages.error(request, json.dumps({"status": result["status"],"title": result["title"], "message": result["message"]}))
            
        return redirect("establishment:public_agenda", uid=uid)
