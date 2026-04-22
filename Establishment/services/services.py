from datetime import datetime, timedelta
from collections import defaultdict
from services.models import Appointment, Diverses, MonthAvailability, Service
from  ..exceps_establishment import EstablishmentNotFound, EstablishmentInactive, EstablishmentIncomplete
import json
from django.shortcuts import get_object_or_404
from ..models import Establishment


class HomeService:
    @staticmethod
    def get_context_establishment(uid):
        establishment = Establishment.objects.filter(uid=uid).first()
        if not establishment:
            print(f"Estabelecimento com UID {uid} não encontrado.")
            raise EstablishmentNotFound()
        
        users = establishment.users.all()
        if not users:
            print(f"Estabelecimento {establishment.name} sem usuários associados.")
            raise EstablishmentIncomplete()
        context = {
            'uid': uid,
            "users": users,
            # Configurações de horário por usuário (início, fim, intervalo)
            "config_json":            HomeService.get_config(users),
            # Agendamentos existentes: {user_id: {date: [{inicio, fim}]}}
            "agendamentos_json":      HomeService.get_appointments(users),
            # Meses disponíveis
            "meses_disponiveis_json": HomeService.get_available_months(users),
            # Serviços
            "servicos_json":          HomeService.get_services(users),
        }
        return context

    # ── CONFIGURAÇÃO DE HORÁRIO ───────────────────────────────────────────────
    @staticmethod
    def get_config(users):
        result = {}
        for user in users:
            diverses = Diverses.objects.filter(user=user).first()
            if not diverses:
                print(f"Estabelecimento {user.establishment.name} sem configuração de horário.")
                raise EstablishmentIncomplete()
            result[str(user.id)] = {
                "hora_inicio":   "09:00",
                "hora_fim":      "18:00",
                "interval_time": diverses.interval_time,
            }
        return json.dumps(result)

    # ── AGENDAMENTOS EXISTENTES ───────────────────────────────────────────────
    @staticmethod
    def get_appointments(users):
        result = {}
        hoje = datetime.now().date()

        for user in users:
            dias = defaultdict(list)

            agendamentos = (
                Appointment.objects
                .filter(user=user, date__gte=hoje)
                .select_related('service')
            )

            for ag in agendamentos:
                inicio_dt = datetime.combine(ag.date, ag.time)
                fim_dt    = inicio_dt + timedelta(minutes=ag.duration)

                dias[str(ag.date)].append({
                    "inicio": ag.time.strftime("%H:%M"),
                    "fim":    fim_dt.strftime("%H:%M"),
                })

            result[str(user.id)] = {
                day: sorted(slots, key=lambda x: x["inicio"])
                for day, slots in dias.items()
            }

        return json.dumps(result)

    # ── MESES DISPONÍVEIS ─────────────────────────────────────────────────────
    @staticmethod
    def get_available_months(users):
        result = {}
        for user in users:
            months = MonthAvailability.objects.filter(availability=True, user=user)
            
            result[str(user.id)] = [
                {"ano": m.year, "mes": m.month}
                for m in months
            ]
        return json.dumps(result)

    # ── SERVIÇOS ──────────────────────────────────────────────────────────────
    @staticmethod
    def get_services(users):
        result = {}
        for user in users:
            result[str(user.id)] = [
                {
                    "id":      s.id,
                    "nome":    s.name,
                    "preco":   str(s.price),
                    "duracao": s.time_duration,
                }
                for s in user.services.all()
            ]
        return json.dumps(result)