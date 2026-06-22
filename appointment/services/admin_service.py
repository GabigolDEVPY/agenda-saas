from django.db import transaction
from datetime import datetime, timedelta

from appointment.models import Appointment


class AppointmentAdminService:
    ACTIVE_STATUSES = (
        Appointment.Status.PENDING,
        Appointment.Status.CONFIRMED,
    )

    @staticmethod
    def get_confirmed_appointments(user):
        return (
            Appointment.objects
            .filter(user=user, status=Appointment.Status.CONFIRMED)
            .select_related("service")
            .order_by("date", "time")
        )

    @staticmethod
    def get_pending_appointments(user):
        return (
            Appointment.objects
            .filter(user=user, status=Appointment.Status.PENDING)
            .select_related("service")
            .order_by("date", "time")
        )

    @staticmethod
    def get_canceled_appointments(user):
        return (
            Appointment.objects
            .filter(user=user, status=Appointment.Status.CANCELED)
            .select_related("service")
            .order_by("-date", "-time")
        )

    @staticmethod
    def get_appointment_for_user(user, pk):
        return (
            Appointment.objects
            .select_related('service', 'user')
            .get(pk=pk, user=user)
        )

    @staticmethod
    def delete_appointment(user, pk):
        appointment = AppointmentAdminService.get_appointment_for_user(user, pk)
        appointment.delete()
        
    @staticmethod
    def delete_appointment_api(session_key, pk):
        appointment = Appointment.objects.filter(pk=pk, session_key=session_key).first()
        if appointment:
            appointment.status = Appointment.Status.CANCELED
            appointment.save(update_fields=["status"])
        appointments = Appointment.objects.filter(session_key=session_key)
        return appointments

    @staticmethod
    def confirm_appointment(user, pk):
        with transaction.atomic():
            appointment = (
                Appointment.objects
                .select_for_update()
                .select_related('service', 'user')
                .get(pk=pk, user=user, status=Appointment.Status.PENDING)
            )

            novo_inicio = datetime.combine(appointment.date, appointment.time)
            novo_fim = novo_inicio + timedelta(minutes=appointment.duration)

            conflitos = Appointment.objects.select_for_update().filter(
                user=user,
                date=appointment.date,
                status__in=AppointmentAdminService.ACTIVE_STATUSES,
            ).exclude(pk=appointment.pk)

            for ag in conflitos:
                ag_inicio = datetime.combine(ag.date, ag.time)
                ag_fim = ag_inicio + timedelta(minutes=ag.duration)
                if novo_inicio < ag_fim and novo_fim > ag_inicio:
                    raise ValueError("Este horário conflita com outro agendamento ativo.")

            appointment.status = Appointment.Status.CONFIRMED
            appointment.save(update_fields=["status"])
            return appointment

    @staticmethod
    def reject_appointment(user, pk):
        appointment = AppointmentAdminService.get_appointment_for_user(user, pk)
        appointment.status = Appointment.Status.REJECTED
        appointment.save(update_fields=["status"])
        return appointment

    @staticmethod
    def appointments_panel_context(user):
        return {
            "pending_appointments": AppointmentAdminService.get_pending_appointments(user),
            "appointments": AppointmentAdminService.get_confirmed_appointments(user),
            "canceled_appointments": AppointmentAdminService.get_canceled_appointments(user),
        }
