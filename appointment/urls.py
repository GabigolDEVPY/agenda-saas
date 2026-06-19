from django.urls import path
from .views import (
    CreateAppointmentView,
    ConfigAgendaView,
    AppointmentDetailView,
    DeleteAppointmentView,
    DeleteAppointmentViewApi,
    ConfirmAppointmentView,
    RejectAppointmentView,
)


app_name = 'appointment'

urlpatterns = [
    path('agendar/', CreateAppointmentView.as_view(), name='agendar'),
    path('config-agenda/', ConfigAgendaView.as_view(), name='config_agenda'),
    path('<int:pk>/detail/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/delete/', DeleteAppointmentView.as_view(), name='delete_appointment'),
    path('<int:pk>/confirm/', ConfirmAppointmentView.as_view(), name='confirm_appointment'),
    path('<int:pk>/reject/', RejectAppointmentView.as_view(), name='reject_appointment'),
    
    # api para deletar agendamento sem htmx, usado na tela de agendamento do cliente
    path('<int:pk>/cliente/delete/', DeleteAppointmentViewApi.as_view(), name='delete_appointment_cliente'),
]
