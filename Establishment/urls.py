from django.urls import path
from . views import PublicAgenda, SaveInfosView

app_name = 'establishment'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    path('infos/save/', SaveInfosView.as_view(), name='save_infos'),
]

