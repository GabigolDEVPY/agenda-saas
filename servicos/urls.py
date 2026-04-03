from django.urls import path
from . views import ServicosView, CreateAppointmentView


app_name = 'servicos'

urlpatterns = [
    path('', ServicosView.as_view(), name='home'),
    path('agendar/', CreateAppointmentView.as_view(), name='agendar'),
]
