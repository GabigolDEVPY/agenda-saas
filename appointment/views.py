import json
from django.shortcuts import redirect
from django.views.generic import View
from django.http import HttpResponse
from .services import AppointmentService
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import MonthAvailability, HoursUnavailable
import datetime
import calendar
from establishment.models import OperatingHours

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

        # Apply backend OperatingHours constraints
        operating_hours = OperatingHours.objects.filter(establishment__user=request.user)
        oh_dict = {item.day_of_week: item for item in operating_hours}
        _, days_in_month = calendar.monthrange(ano, mes)

        for d in range(1, days_in_month + 1):
            date_obj = datetime.date(ano, mes, d)
            # Python weekday(): 0=Mon, 6=Sun matches Model day_of_week: 0=Segunda, 6=Domingo
            dow = date_obj.weekday()
            oh = oh_dict.get(dow)
            
            date_str = f"{ano}-{mes:02d}-{d:02d}"
            
            if not oh or oh.is_closed:
                # Force dia off
                if date_str not in dias_off:
                    dias_off.append(date_str)
                # Remove from horarios if it's there
                horarios.pop(date_str, None)
            else:
                # Add out-of-bounds slots to 'horarios' blocked list
                # Generate all possible 30-min slots from 06:00 to 22:30
                # and if they fall outside oh.open_time and oh.close_time, block them.
                all_slots = []
                h, m_val = 6, 0
                while h < 23:
                    all_slots.append(f"{h:02d}:{m_val:02d}")
                    m_val += 30
                    if m_val >= 60:
                        m_val -= 60
                        h += 1
                
                open_str = oh.open_time.strftime('%H:%M') if oh.open_time else '09:00'
                close_str = oh.close_time.strftime('%H:%M') if oh.close_time else '18:00'
                
                if date_str not in dias_off:
                    if date_str not in horarios:
                        horarios[date_str] = []
                    
                    for slot in all_slots:
                        if slot < open_str or slot >= close_str:
                            if slot not in horarios[date_str]:
                                horarios[date_str].append(slot)

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
