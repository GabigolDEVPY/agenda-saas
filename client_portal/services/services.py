from datetime import datetime, timedelta
from collections import defaultdict
from appointment.models import Appointment, MonthAvailability
import json
from establishment.models import Establishment
from establishment.services.messages import ERRORS
from .utils import group_operating_hours

class HomeService:
    @staticmethod
    def get_config(users):
        result = {}
        for user in users:
            establishment = getattr(user, "establishment", None)
            horarios_funcionamento = HomeService._get_operating_hours_config(establishment)
            primeiro_dia_aberto = next(
                (dia for dia in horarios_funcionamento.values() if dia["aberto"]),
                {"inicio": "09:00", "fim": "18:00"},
            )

            result[str(user.id)] = {
                "hora_inicio": primeiro_dia_aberto["inicio"],
                "hora_fim": primeiro_dia_aberto["fim"],
                "horarios_funcionamento": horarios_funcionamento,
            }
        return json.dumps(result)

    @staticmethod
    def _get_operating_hours_config(establishment):
        defaults = {
            str(day): {"aberto": day != 0, "inicio": "09:00", "fim": "18:00"}
            for day in range(7)
        }

        if not establishment:
            return defaults

        horarios = defaults.copy()
        django_to_js_day = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}

        for item in establishment.operating_hours.all():
            js_day = django_to_js_day.get(item.day_of_week)
            if js_day is None:
                continue

            horarios[str(js_day)] = {
                "aberto": not item.is_closed,
                "inicio": item.open_time.strftime("%H:%M"),
                "fim": item.close_time.strftime("%H:%M"),
            }

        return horarios

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

    @staticmethod
    def get_infos_establishment(establishment):
        result = {
            "location": establishment.address,
            "phone": establishment.phone,
            "operating_hours_grouped": group_operating_hours(establishment.operating_hours.all())
        }
        print(result["operating_hours_grouped"])
        return result


    @staticmethod
    def get_context_establishment(uid):
        establishment = Establishment.objects.filter(uid=uid).first()
        if not establishment or not establishment.general_preferences.open_establishment:
            return {"msg": ERRORS["ESTABLISHMENT_NOT_FOUND"], "incomplete": True}



        users = establishment.users.all()
        if not users:
            return {"msg": ERRORS["ESTABLISHMENT_INCOMPLETE"], "incomplete": True}
        
        context = {
            'uid': uid,
            "users": users,
            "config_json": HomeService.get_config(users),
            "agendamentos_json": HomeService.get_appointments(users),
            "meses_disponiveis_json": HomeService.get_available_months(users),
            "servicos_json": HomeService.get_services(users),
            "infos": HomeService.get_infos_establishment(establishment),
            "gereral_preferences": establishment.general_preferences
        }
        print(context["servicos_json"])
        return context

