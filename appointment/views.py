import json
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import AppointmentService, ConfigAgendaService, AppointmentAdminService
from .models import Appointment


class CreateAppointmentView(View):
    def post(self, request):
        errors, result = AppointmentService.create_appointment(request.POST)

        if not result:
            messages.error(request, json.dumps({
                "status": "error", "title": "Erro de validação", "message": str(errors),
            }))
            return redirect(request.META.get("HTTP_REFERER"))

        uid = result["uid"]
        if result.get("status") == "success":
            messages.success(request, json.dumps({
                "status": result["status"],
                "horario": result["horario"],
                "title": result["title"],
                "message": result["message"],
            }))
        else:
            messages.error(request, json.dumps({
                "status": result["status"],
                "title": result["title"],
                "message": result["message"],
            }))

        return redirect("client_portal:public_agenda", uid=uid)


class ConfigAgendaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            ConfigAgendaService.save_month_config(request.user, request.POST)
        except ValueError:
            return HttpResponse(status=400)
        return HttpResponse(status=200)


class AppointmentDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        appointment = get_object_or_404(
            Appointment.objects.select_related('service', 'user'),
            pk=pk,
            user=request.user,
        )
        return render(
            request,
            'partials/appointments/appointment_detail_modal.html',
            {'appointment': appointment},
        )


class DeleteAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        AppointmentAdminService.delete_appointment(request.user, pk)
        return _hx_appointments_response(request, 'appointmentDeleted')


class ConfirmAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            AppointmentAdminService.confirm_appointment(request.user, pk)
        except (Appointment.DoesNotExist, ValueError):
            return HttpResponse(status=400)
        return _hx_appointments_response(request, 'appointmentUpdated')


class RejectAppointmentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        AppointmentAdminService.reject_appointment(request.user, pk)
        return _hx_appointments_response(request, 'appointmentUpdated')


def _hx_appointments_response(request, trigger):
    if not request.headers.get('HX-Request'):
        return redirect('admin_portal:home')

    response = render(
        request,
        'partials/appointments/appointments_panel_inner.html',
        AppointmentAdminService.appointments_panel_context(request.user),
    )
    response['HX-Trigger'] = trigger
    return response
