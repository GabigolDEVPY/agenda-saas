import json
import datetime

from appointment.models import MonthAvailability, HoursUnavailable, DayUnavailable


class ConfigAgendaService:
    @staticmethod
    def save_month_config(user, post_data):
        ano = post_data.get('ano')
        mes = post_data.get('mes')
        dias_off_json = post_data.get('dias_off', '[]')
        horarios_json = post_data.get('horarios', '{}')

        try:
            dias_off = json.loads(dias_off_json)
            horarios = json.loads(horarios_json)
            ano = int(ano)
            mes = int(mes) + 1
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            raise ValueError(f"Dados inválidos: {exc}") from exc

        month_avail, _ = MonthAvailability.objects.get_or_create(
            user=user,
            year=ano,
            month=mes,
        )
        month_avail.availability = True
        month_avail.save()

        DayUnavailable.objects.filter(user=user, month=month_avail).delete()
        HoursUnavailable.objects.filter(user=user, month=month_avail).delete()

        days_to_create = []
        for date_str in dias_off:
            day = int(date_str.split('-')[2])
            days_to_create.append(DayUnavailable(
                user=user,
                month=month_avail,
                day=day,
            ))

        hours_to_create = []
        for date_str, slots in horarios.items():
            day = int(date_str.split('-')[2])
            for slot in slots:
                h, m = map(int, slot.split(':'))
                hours_to_create.append(HoursUnavailable(
                    user=user,
                    month=month_avail,
                    day=day,
                    hour=datetime.time(h, m),
                ))

        if days_to_create:
            DayUnavailable.objects.bulk_create(days_to_create)
        if hours_to_create:
            HoursUnavailable.objects.bulk_create(hours_to_create)
