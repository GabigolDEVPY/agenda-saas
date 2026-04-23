from django.urls import path
from . views import PublicAgenda, SaveInfosView, SaveAddressView

app_name = 'establishment'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    path('infos/save/', SaveInfosView.as_view(), name='save_infos'),
    path('address/save/', SaveAddressView.as_view(), name='save_address'),

    # alter operating days and hours
    path('operating/day-alter', SaveInfosView.as_view(), name='day_alter'),
    path('operating/day-open', SaveInfosView.as_view(), name='day_open'),
    path('operating/day-close', SaveInfosView.as_view(), name='day_close'),
]

