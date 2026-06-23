import json
import datetime

from django.db import transaction
from django.utils import timezone

from appointment.forms import AppointmentForm
from appointment.models import Appointment, DayUnavailable, HoursUnavailable
from billing.services import LimitsService
from client_portal.services.services import HomeService
from establishment.models import Establishment
from user.models import Preferences

from .utils import error, operating_hours_for_date, to_min


ACTIVE_STATUSES = (
    Appointment.Status.PENDING,
    Appointment.Status.CONFIRMED,
)


def _add_slots_in_interval(slots, start_min, end_min, duration):
    if end_min - start_min < duration:
        return

    cursor = start_min
    while cursor + duration <= end_min:
        slots.add(cursor)
        cursor += duration


def _available_slot_minutes(start_min, end_min, duration, appointments):
    slots = set()
    cursor_free = start_min

    ordered_appointments = sorted(
        appointments,
        key=lambda appointment: to_min(appointment.time.strftime("%H:%M")),
    )

    for appointment in ordered_appointments:
        appointment_start = to_min(appointment.time.strftime("%H:%M"))
        appointment_end = appointment_start + appointment.duration

        if appointment_end <= start_min or appointment_start >= end_min:
            continue

        _add_slots_in_interval(slots, cursor_free, min(appointment_start, end_min), duration)
        if appointment_end > cursor_free:
            cursor_free = appointment_end

    _add_slots_in_interval(slots, cursor_free, end_min, duration)
    return slots


class BookingService:
    @staticmethod
    def create_appointment(form_data, session_key):
        form = AppointmentForm(form_data)

        if not form.is_valid():
            erro = next(iter(form.errors.values()))[0]
            return erro, False

        user = form.cleaned_data['user']
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']
        service = form.cleaned_data['service']

        establishment = Establishment.objects.filter(id=user.establishment.id).first()
        if not establishment or not establishment.general_preferences.open_establishment:
            return "Estabelecimento fechado", False

        can_use_agenda, billing_message = LimitsService.public_agenda_status(establishment)
        if not can_use_agenda:
            return billing_message, False

        horario_str = time.strftime("%H:%M")
        uid = str(user.establishment.uid)

        if service.user_id != user.id or not service.is_active:
            return None, error(uid, horario_str, "Servico indisponivel", "Esse servico nao esta disponivel para agendamento")

        agora = timezone.localtime(timezone.now())
        if date == agora.date() and time <= agora.time():
            return None, error(uid, horario_str, "Horário Inválido", "Esse horário já passou")

        user_id = str(user.id)
        data_str = str(date)
        duration_snapshot = service.time_duration
        novo_inicio = datetime.datetime.combine(date, time)
        novo_fim = novo_inicio + datetime.timedelta(minutes=duration_snapshot)

        config = json.loads(HomeService.get_config([user]))
        cfg = config.get(user_id, {})

        operating_hours = operating_hours_for_date(cfg, date)
        if not operating_hours or not operating_hours["aberto"]:
            return None, error(uid, horario_str, "Horario Invalido", "Esse dia esta fora do horario de funcionamento")

        hora_inicio_min = to_min(operating_hours["inicio"])
        hora_fim_min = to_min(operating_hours["fim"])
        slot_inicio_min = to_min(horario_str)
        slot_fim_min = slot_inicio_min + duration_snapshot
        effective_interval = duration_snapshot

        if slot_inicio_min < hora_inicio_min or slot_fim_min > hora_fim_min:
            return None, error(uid, horario_str, "Horário Inválido", "Esse horário está fora do horário de funcionamento")

        if DayUnavailable.objects.filter(
            user=user,
            month__year=date.year,
            month__month=date.month,
            day=date.day,
        ).exists():
            return None, error(
                uid, horario_str,
                "Dia Indisponível",
                "O profissional não está disponível neste dia"
            )

        hours_unavailable = HoursUnavailable.objects.filter(
            user=user,
            month__year=date.year,
            month__month=date.month,
            day=date.day,
        )

        for hu in hours_unavailable:
            hu_min = to_min(hu.hour.strftime('%H:%M'))
            if slot_inicio_min <= hu_min < slot_fim_min:
                return None, error(
                    uid, horario_str,
                    "Horário Indisponível",
                    "Esse horário foi bloqueado pelo profissional"
                )

        agendamentos_para_validacao = Appointment.objects.filter(
            user=user,
            date=date,
            status__in=ACTIVE_STATUSES,
        )
        
        available_slots = _available_slot_minutes(
            hora_inicio_min,
            hora_fim_min,
            duration_snapshot,
            agendamentos_para_validacao
        )
        
        if slot_inicio_min not in available_slots:
            return None, error(uid, horario_str, "Horário Inválido", "Esse horário não está disponível")

        preferences, _ = Preferences.objects.get_or_create(user=user)
        active_count = Appointment.objects.filter(
            user=user,
            date=date,
            status__in=ACTIVE_STATUSES,
        ).count()
        if active_count >= preferences.max_appointments:
            return None, error(
                uid, horario_str,
                "Limite Atingido",
                f"Este profissional já atingiu o limite de {preferences.max_appointments} agendamento(s) neste dia"
            )

        with transaction.atomic():
            agendamentos_db = Appointment.objects.select_for_update().filter(
                user=user,
                date=date,
                status__in=ACTIVE_STATUSES,
            )

            if agendamentos_db.count() >= preferences.max_appointments:
                return None, error(
                    uid, horario_str,
                    "Limite Atingido",
                    f"Este profissional já atingiu o limite de {preferences.max_appointments} agendamento(s) neste dia"
                )

            for ag in agendamentos_db:
                ag_inicio = datetime.datetime.combine(date, ag.time)
                ag_fim = ag_inicio + datetime.timedelta(minutes=ag.duration)
                if novo_inicio < ag_fim and novo_fim > ag_inicio:
                    return None, error(uid, horario_str, "Agendamento Inválido", "Esse horário conflita com outro agendamento")

            appointment = form.save(commit=False)
            appointment.duration = duration_snapshot
            appointment.total = service.price
            appointment.session_key = session_key
            if preferences.confirm_manually_appointments:
                appointment.status = Appointment.Status.PENDING
            else:
                appointment.status = Appointment.Status.CONFIRMED
            appointment.save()

        # abaixo feature para adicionar id em session do usuário

        
        if appointment.status == Appointment.Status.PENDING:
            
            return None, {
                "status": "success",
                "horario": horario_str,
                "title": "Solicitação enviada!",
                "message": f"Sua solicitação para {service.name} às {horario_str} foi enviada. Aguarde a confirmação do profissional.",
                "uid": uid,
            }

        return None, {
            "status": "success",
            "horario": horario_str,
            "title": "Agendamento criado!",
            "message": f"Seu horário para {service.name} às {horario_str} foi reservado com sucesso.",
            "uid": uid,
        }
