from django.urls import path
from . views import ServicesView, CreateAppointmentView


app_name = 'services'

urlpatterns = [
    path('', ServicesView.as_view(), name='home'),
    path('agendar/', CreateAppointmentView.as_view(), name='agendar'),
]
