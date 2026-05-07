from django.urls import path
from . views import PublicAgenda, SaveAddressView, SaveInfosView, SaveOperatingHoursView

app_name = 'establishment'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    ]