from servicos.forms import AppointmentForm
from datetime import datetime, timedelta
from .models import Appointment
from Establishment.services import HomeService
import json


class AppointmentService:
    @staticmethod
    def create_appointment(form):
        form = AppointmentForm(form)

        if not form.is_valid():
            erro = next(iter(form.errors.values()))[0]
            return erro, False

        employee = form.cleaned_data['employee']
        date     = form.cleaned_data['date']
        time     = form.cleaned_data['time']
        service  = form.cleaned_data['service']

        horario_str  = time.strftime("%H:%M")
        employee_id  = str(employee.id)
        data_str     = str(date)

        # ── Captura a duração atual do serviço no momento do agendamento ──────
        duration_snapshot = service.time_duration

        novo_inicio = datetime.combine(date, time)
        novo_fim    = novo_inicio + timedelta(minutes=duration_snapshot)

        # ── Carrega agendamentos existentes do dia via HomeService ────────────
        agendamentos_json = json.loads(
            HomeService.get_agendamentos([employee])
        )

        agendamentos_dia = agendamentos_json.get(employee_id, {}).get(data_str, [])

        # ── Valida conflito contra os agendamentos reais ──────────────────────
        for ag in agendamentos_dia:
            ag_inicio = datetime.combine(date, datetime.strptime(ag['inicio'], "%H:%M").time())
            ag_fim    = datetime.combine(date, datetime.strptime(ag['fim'],    "%H:%M").time())

            if novo_inicio < ag_fim and novo_fim > ag_inicio:
                return None, {
                    "status":  "error",
                    "horario": horario_str,
                    "title":   "Agendamento Inválido",
                    "message": "Esse horário conflita com outro agendamento",
                    "uid":     str(employee.establishment.uid),
                }

        # ── Carrega configuração do funcionário ───────────────────────────────
        config = json.loads(HomeService.get_config([employee]))
        cfg    = config.get(employee_id, {})

        hora_inicio_min = _to_min(cfg.get('hora_inicio', '09:00'))
        hora_fim_min    = _to_min(cfg.get('hora_fim',    '18:00'))
        slot_inicio_min = _to_min(horario_str)
        slot_fim_min    = slot_inicio_min + duration_snapshot

        # ── Valida se o horário é um slot válido (não quebrado) ───────────────
        slot_interval = cfg.get('slot_interval', 30)
        offset        = slot_inicio_min - hora_inicio_min

        if offset % slot_interval != 0:
            return None, {
                "status":  "error",
                "horario": horario_str,
                "title":   "Horário Inválido",
                "message": "Esse horário não corresponde a um slot disponível",
                "uid":     str(employee.establishment.uid),
            }

        # ── Valida se o slot está dentro do horário de funcionamento ──────────
        if slot_inicio_min < hora_inicio_min or slot_fim_min > hora_fim_min:
            return None, {
                "status":  "error",
                "horario": horario_str,
                "title":   "Horário Inválido",
                "message": "Esse horário está fora do horário de funcionamento",
                "uid":     str(employee.establishment.uid),
            }

        # ── Salva gravando a duração do momento do agendamento ────────────────
        appointment = form.save(commit=False)
        appointment.duration = duration_snapshot
        appointment.save()

        return None, {
            "status":  "success",
            "horario": horario_str,
            "title":   "Agendamento criado!",
            "message": f"Seu horário para {service.name} às {horario_str} foi reservado com sucesso.",
            "uid":     str(employee.establishment.uid),
        }


def _to_min(hhmm: str) -> int:
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)