from django.urls import path
from . views import PublicAgenda, Appointments

app_name = 'client_portal'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    path('appointments/', Appointments.as_view(), name='appointments'),
    ]