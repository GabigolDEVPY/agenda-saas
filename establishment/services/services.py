from datetime import datetime, timedelta
from collections import defaultdict
from services.models import Appointment, Diverses, MonthAvailability
import json
from ..models import Establishment
from establishment.services.messages import ERRORS, SUCCESS

class HomeService:
    @staticmethod
    def get_context_establishment(uid):
        establishment = Establishment.objects.filter(uid=uid).first()
        if not establishment:
            return {"msg": ERRORS["ESTABLISHMENT_NOT_FOUND"], "incomplete": True}
        
        users = establishment.users.all()
        if not users:
            return {"msg": ERRORS["ESTABLISHMENT_INCOMPLETE"], "incomplete": True}
        context = {
            'uid': uid,
            "users": users,
            # Configurações de horário por usuário (início, fim, intervalo)
            "config_json": HomeService.get_config(users),
            # Agendamentos existentes: {user_id: {date: [{inicio, fim}]}}
            "agendamentos_json": HomeService.get_appointments(users),
            # Meses disponíveis
            "meses_disponiveis_json": HomeService.get_available_months(users),
            # Serviços
            "servicos_json": HomeService.get_services(users),
        }
        return context

    # ── CONFIGURAÇÃO DE HORÁRIO ───────────────────────────────────────────────
    @staticmethod
    def get_config(users):
        result = {}
        for user in users:
            diverses = Diverses.objects.filter(user=user).first()
            if not diverses:
                return {"msg": ERRORS["ESTABLISHMENT_INCOMPLETE"], "incomplete": True}
            result[str(user.id)] = {
                "hora_inicio": "09:00",
                "hora_fim": "18:00",
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
                fim_dt = inicio_dt + timedelta(minutes=ag.duration)

                dias[str(ag.date)].append({
                    "inicio": ag.time.strftime("%H:%M"),
                    "fim": fim_dt.strftime("%H:%M"),
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
        has_service = False

        for user in users:
            services = [
                {
                    "id": s.id,
                    "nome": s.name,
                    "preco": str(s.price),
                    "duracao": s.time_duration,
                }
                for s in user.services.all()
            ]


            result[str(user.id)] = services



        return json.dumps(result)
