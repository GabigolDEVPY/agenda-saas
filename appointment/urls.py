from django.urls import path
from . views import CreateAppointmentView, ConfigAgendaView


app_name = 'appointment'

urlpatterns = [
    path('agendar/', CreateAppointmentView.as_view(), name='agendar'),
    path('config-agenda/', ConfigAgendaView.as_view(), name='config_agenda'),
]
