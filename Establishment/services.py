from datetime import datetime, timedelta, time, date
from collections import defaultdict
from servicos.models import Appointment, Diverses, MonthAvailability, Service
import calendar
import json
from django.shortcuts import render, get_object_or_404
from .models import Establishment
 
 
class HomeService:
    @staticmethod
    def get_context_establishment(uid):
        establishment = get_object_or_404(Establishment, uid=uid)
        employees = establishment.employees.all()
 
        context = {
            'uid': uid,
            "employees": employees,
            # Configurações de horário por barbeiro (início, fim, intervalo)
            "config_json":            HomeService.get_config(employees),
            # Agendamentos existentes: {employee_id: {date: [{inicio, fim}]}}
            "agendamentos_json":      HomeService.get_agendamentos(employees),
            # Meses disponíveis (mantido igual)
            "meses_disponiveis_json": HomeService.get_available_months(employees),
            # Serviços (mantido igual)
            "servicos_json":          HomeService.get_servicos(employees),
        }
        return context
 
    # ── CONFIGURAÇÃO DE HORÁRIO ───────────────────────────────────────────────
    # Retorna para cada barbeiro: hora_inicio, hora_fim e interval_time
    # O frontend usa isso para gerar os slots dinamicamente.
    @staticmethod
    def get_config(employees):
        result = {}
        for employee in employees:
            diverses = Diverses.objects.get(employee=employee)
            result[str(employee.id)] = {
                "hora_inicio":   "09:00",   # ajuste conforme seu modelo
                "hora_fim":      "18:00",   # ajuste conforme seu modelo
                "interval_time": diverses.interval_time,  # minutos (ex: 30)
            }
        return json.dumps(result)
 
    # ── AGENDAMENTOS EXISTENTES ───────────────────────────────────────────────
    # Retorna todos os agendamentos futuros com início e fim reais.
    # O frontend usa isso para saber quais janelas estão bloqueadas.
    #
    # Formato: {
    #   "<employee_id>": {
    #     "YYYY-MM-DD": [
    #       {"inicio": "09:30", "fim": "10:10"},
    #       ...
    #     ]
    #   }
    # }
    @staticmethod
    def get_agendamentos(employees):
        result = {}
        hoje = datetime.now().date()
 
        for employee in employees:
            dias = defaultdict(list)
 
            agendamentos = (
                Appointment.objects
                .filter(employee=employee, date__gte=hoje)
                .select_related('service')
            )
 
            for ag in agendamentos:
                inicio_dt = datetime.combine(ag.date, ag.time)
                fim_dt    = inicio_dt + timedelta(minutes=ag.duration)  # ← era ag.service.time_duration

                dias[str(ag.date)].append({
                    "inicio": ag.time.strftime("%H:%M"),
                    "fim":    fim_dt.strftime("%H:%M"),
                })
 
            # Ordena por horário de início em cada dia
            result[str(employee.id)] = {
                day: sorted(slots, key=lambda x: x["inicio"])
                for day, slots in dias.items()
            }
 
        return json.dumps(result)
 
    # ── MESES DISPONÍVEIS ─────────────────────────────────────────────────────
    @staticmethod
    def get_available_months(employees):
        result = {}
        for employee in employees:
            months = MonthAvailability.objects.filter(availability=True, employee=employee)
            result[str(employee.id)] = [
                {"ano": m.year, "mes": m.month}
                for m in months
            ]
        return json.dumps(result)
 
    # ── SERVIÇOS ──────────────────────────────────────────────────────────────
    @staticmethod
    def get_servicos(employees):
        result = {}
        for employee in employees:
            result[str(employee.id)] = [
                {
                    "id":      s.id,
                    "nome":    s.name,
                    "preco":   str(s.price),
                    "duracao": s.time_duration,
                }
                for s in employee.services.all()
            ]
        return json.dumps(result)