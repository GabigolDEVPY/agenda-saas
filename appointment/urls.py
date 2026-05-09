from django.urls import path
from . views import CreateAppointmentView


app_name = 'appointment'

urlpatterns = [
    path('agendar/', CreateAppointmentView.as_view(), name='agendar'),
]
