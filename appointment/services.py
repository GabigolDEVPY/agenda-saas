from appointment.forms import AppointmentForm
from datetime import datetime, timedelta
from establishment.models import Establishment
from .models import Appointment
from django.db import transaction
from django.utils import timezone
import json
from client_portal.services.services import HomeService


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

        # Verificar se establishment está ativo
        establishment = Establishment.objects.filter(id=user.establishment.id).first()
        if not establishment or not establishment.general_preferences.open_establishment:
            return "Estabelecimento fechado", False

        horario_str = time.strftime("%H:%M")
        uid = str(user.establishment.uid)

        if service.user_id != user.id or not service.is_active:
            return None, _error(uid, horario_str, "Servico indisponivel", "Esse servico nao esta disponivel para agendamento")

        agora = timezone.localtime(timezone.now())
        if date == agora.date() and time <= agora.time():
            return None, _error(uid, horario_str, "Horário Inválido", "Esse horário já passou")

        user_id = str(user.id)
        data_str = str(date)
        duration_snapshot = service.time_duration
        novo_inicio = datetime.combine(date, time)
        novo_fim = novo_inicio + timedelta(minutes=duration_snapshot)

        # Validações de grade e expediente (sem lock, só leitura)
        config = json.loads(HomeService.get_config([user]))
        cfg = config.get(user_id, {})

        operating_hours = _operating_hours_for_date(cfg, date)
        if not operating_hours or not operating_hours["aberto"]:
            return None, _error(uid, horario_str, "Horario Invalido", "Esse dia esta fora do horario de funcionamento")

        hora_inicio_min = _to_min(operating_hours["inicio"])
        hora_fim_min    = _to_min(operating_hours["fim"])
        slot_inicio_min = _to_min(horario_str)
        slot_fim_min    = slot_inicio_min + duration_snapshot
        effective_interval = duration_snapshot

        # Verificar horário de funcionamento
        if slot_inicio_min < hora_inicio_min or slot_fim_min > hora_fim_min:
            return None, _error(uid, horario_str, "Horário Inválido", "Esse horário está fora do horário de funcionamento")

        # Busca términos de agendamentos existentes para permitir continuação natural
        agendamentos_json = json.loads(HomeService.get_appointments([user]))
        agendamentos_dia  = agendamentos_json.get(user_id, {}).get(data_str, [])
        ends_of_existing  = {_to_min(ag['fim']) for ag in agendamentos_dia}

        # Horário válido se segue a duração do serviço ou continua um agendamento existente.
        offset = slot_inicio_min - hora_inicio_min
        on_service_grid      = (offset % effective_interval == 0)
        is_natural_continuation = slot_inicio_min in ends_of_existing

        if not on_service_grid and not is_natural_continuation:
            return None, _error(uid, horario_str, "Horário Inválido", "Esse horário não corresponde a um slot disponível")

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
                    return None, _error(uid, horario_str, "Agendamento Inválido", "Esse horário conflita com outro agendamento")

            appointment          = form.save(commit=False)
            appointment.duration = duration_snapshot
            appointment.total    = service.price
            appointment.save()

        return None, {
            "status":  "success",
            "horario": horario_str,
            "title":   "Agendamento criado!",
            "message": f"Seu horário para {service.name} às {horario_str} foi reservado com sucesso.",
            "uid":     uid,
        }


def _error(uid: str, horario: str, title: str, message: str) -> dict:
    return {
        "status":  "error",
        "horario": horario,
        "title":   title,
        "message": message,
        "uid":     uid,
    }


def _to_min(hhmm: str) -> int:
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def _operating_hours_for_date(cfg: dict, date):
    horarios = cfg.get("horarios_funcionamento") or {}
    js_day = (date.weekday() + 1) % 7
    day_cfg = horarios.get(str(js_day))

    if day_cfg:
        return day_cfg

    return {
        "aberto": True,
        "inicio": cfg.get("hora_inicio", "09:00"),
        "fim": cfg.get("hora_fim", "18:00"),
    }
