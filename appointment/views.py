import json
from django.shortcuts import redirect
from django.views.generic import View
from django.http import HttpResponse
from .services import AppointmentService
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MonthAvailability, HoursUnavailable
import datetime

class CreateAppointmentView(View):
    def post(self, request):
        errors, result = AppointmentService.create_appointment(request.POST)

        if not result:
            messages.error(request, json.dumps({"status": "error","title": "Erro de validação","message": str(errors) }))
            return redirect(request.META.get("HTTP_REFERER"))

        elif result and result.get("status") == "success":
            uid = result["uid"]
            messages.success(request, json.dumps({"status": result["status"],"horario": result["horario"],"title": result["title"],"message": result["message"]}))


        elif result:
            uid = result["uid"]
            messages.error(request, json.dumps({"status": result["status"],"title": result["title"], "message": result["message"]}))
            
        return redirect("client_portal:public_agenda", uid=uid)

class ConfigAgendaView(LoginRequiredMixin, View):
    def post(self, request):
        ano = request.POST.get('ano')
        mes = request.POST.get('mes')
        print(mes, ano)
        dias_off_json = request.POST.get('dias_off', '[]')
        horarios_json = request.POST.get('horarios', '{}')
        print(dias_off_json)
        print(horarios_json)
        
        try:
            dias_off = json.loads(dias_off_json)
            horarios = json.loads(horarios_json)
            ano = int(ano)
            mes = int(mes) + 1
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error parsing data: {e}, ano={ano}, mes={mes}, dias_off={dias_off_json}, horarios={horarios_json}")
            return HttpResponse(status=400)

        month_avail, _ = MonthAvailability.objects.get_or_create(
            user=request.user,
            year=ano,
            month=mes
        )
        month_avail.availability = True
        month_avail.save()

        HoursUnavailable.objects.filter(user=request.user, month=month_avail).delete()

        dummy_time = datetime.time(0, 0)
        hours_to_create = []
        
        for d in dias_off:
            day = int(d.split('-')[2])
            hours_to_create.append(HoursUnavailable(
                user=request.user,
                month=month_avail,
                day=day,
                hour=dummy_time
            ))
            
        for d, slots in horarios.items():
            day = int(d.split('-')[2])
            for slot in slots:
                h, m = map(int, slot.split(':'))
                time_obj = datetime.time(h, m)
                hours_to_create.append(HoursUnavailable(
                    user=request.user,
                    month=month_avail,
                    day=day,
                    hour=time_obj
                ))
                
        if hours_to_create:
            HoursUnavailable.objects.bulk_create(hours_to_create)

        return HttpResponse(status=200)
