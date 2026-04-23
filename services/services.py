from services.forms import AppointmentForm
from datetime import datetime, timedelta
from .models import Appointment
from establishment.services.services import HomeService
from django.db import transaction
import json
from establishment.models import Establishment, Address, OperatingHours






class AdminService:
    @staticmethod
    def get_context_admin(view, **kwargs):
        context = super(type(view), view).get_context_data(**kwargs)

        uid = view.request.session.get('uid')
        establishment = Establishment.objects.filter(uid=uid).first()

        context['establishment'] = establishment
        context['address'] = Address.objects.filter(establishment=establishment).first() if establishment else None
        context['operating_hours'] = json.dumps(AdminService.get_operating_hours(view, establishment))
        print(context['operating_hours'])

        return context

    @staticmethod
    def get_operating_hours(view, establishment):
            dias_map = {0: 'seg',1: 'ter',2: 'qua',3: 'qui',4: 'sex',5: 'sab',6: 'dom',}

            defaults = {
                'dom': {'aberto': False, 'abertura': '08:00', 'fechamento': '18:00'},
                'seg': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'ter': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'qua': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'qui': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'sex': {'aberto': True,  'abertura': '08:00', 'fechamento': '20:00'},
                'sab': {'aberto': True,  'abertura': '09:00', 'fechamento': '18:00'},
            }
            if not establishment:
                return defaults

            operating_hours = OperatingHours.objects.filter(establishment=establishment).order_by('day_of_week')
            result = defaults.copy()

            for item in operating_hours:
                key = dias_map.get(item.day_of_week)
                if not key:
                    continue

                result[key] = {
                    'aberto': not item.is_closed,'abertura': item.open_time.strftime('%H:%M'),'fechamento': item.close_time.strftime('%H:%M'),
                }

            return result


















class AppointmentService:
    @staticmethod
    def create_appointment(form):
        form = AppointmentForm(form)

        if not form.is_valid():
            erro = next(iter(form.errors.values()))[0]
            return erro, False

        user = form.cleaned_data['user']
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        service = form.cleaned_data['service']

        horario_str = time.strftime("%H:%M")
        user_id = str(user.id)
        data_str = str(date)
        duration_snapshot = service.time_duration
        novo_inicio = datetime.combine(date, time)
        novo_fim = novo_inicio + timedelta(minutes=duration_snapshot)

        # Validações de grade e expediente (sem lock, só leitura)
        config = json.loads(HomeService.get_config([user]))
        cfg = config.get(user_id, {})

        hora_inicio_min = _to_min(cfg.get('hora_inicio', '09:00'))
        hora_fim_min = _to_min(cfg.get('hora_fim',    '18:00'))
        slot_inicio_min = _to_min(horario_str)
        slot_fim_min = slot_inicio_min + duration_snapshot
        slot_interval = cfg.get('slot_interval', 30)

        # Busca términos de agendamentos existentes para permitir continuação natural
        agendamentos_json = json.loads(HomeService.get_appointments([user]))
        agendamentos_dia = agendamentos_json.get(user_id, {}).get(data_str, [])
        ends_of_existing = {_to_min(ag['fim']) for ag in agendamentos_dia}

        on_grid  = ((slot_inicio_min - hora_inicio_min) % slot_interval == 0)
        is_natural_continuation = slot_inicio_min in ends_of_existing

        if not on_grid and not is_natural_continuation:
            return None, {
                "status":  "error",
                "horario": horario_str,
                "title": "Horário Inválido",
                "message": "Esse horário não corresponde a um slot disponível",
                "uid": str(user.establishment.uid),
            }

        if slot_inicio_min < hora_inicio_min or slot_fim_min > hora_fim_min:
            return None, {
                "status": "error",
                "horario": horario_str,
                "title": "Horário Inválido",
                "message": "Esse horário está fora do horário de funcionamento",
                "uid":     str(user.establishment.uid),
            }

        # Checagem de conflito com lock no banco + save atômico
        with transaction.atomic():
            agendamentos_db = Appointment.objects.select_for_update().filter(
                user=user,
                date=date,
            )

            for ag in agendamentos_db:
                ag_inicio = datetime.combine(date, ag.time)
                ag_fim    = ag_inicio + timedelta(minutes=ag.duration)
                if novo_inicio < ag_fim and novo_fim > ag_inicio:
                    return None, {
                        "status":  "error",
                        "horario": horario_str,
                        "title":   "Agendamento Inválido",
                        "message": "Esse horário conflita com outro agendamento",
                        "uid":     str(user.establishment.uid),
                    }

            appointment          = form.save(commit=False)
            appointment.duration = duration_snapshot
            appointment.total    = service.price
            appointment.save()

        return None, {
            "status":  "success",
            "horario": horario_str,
            "title":   "Agendamento criado!",
            "message": f"Seu horário para {service.name} às {horario_str} foi reservado com sucesso.",
            "uid":     str(user.establishment.uid),
        }


def _to_min(hhmm: str) -> int:
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)