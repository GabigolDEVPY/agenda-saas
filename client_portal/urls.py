from django.urls import path
from . views import PublicAgenda

app_name = 'client_portal'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    ]