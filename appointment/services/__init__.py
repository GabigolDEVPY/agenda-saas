from .booking_service import BookingService
from .config_agenda_service import ConfigAgendaService
from .admin_service import AppointmentAdminService

# Alias para compatibilidade
AppointmentService = BookingService

__all__ = [
    "AppointmentService",
    "BookingService",
    "ConfigAgendaService",
    "AppointmentAdminService",
]
